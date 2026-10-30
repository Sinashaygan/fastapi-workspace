"""Run with: venv/bin/python -m unittest discover -s tests -v"""

import os
from pathlib import Path
import sys
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "core"))
os.environ["SQLALCHEMY_DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET_KEY"] = "jwt-regression-test-secret-key-32-bytes"

import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from auth import jwt_auth
from core.config import settings
from core.database import Base, get_db
from main import app
from users.models import UserModel


class JWTAuthenticationTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.sessions = sessionmaker(bind=self.engine)
        with self.sessions() as db:
            db.add(UserModel(id=1, username="test-user", password="unused"))
            db.commit()

        def test_db():
            with self.sessions() as db:
                yield db

        self.previous_overrides = app.dependency_overrides.copy()
        app.dependency_overrides[get_db] = test_db
        self.client = TestClient(app)

    def tearDown(self):
        self.client.close()
        app.dependency_overrides.clear()
        app.dependency_overrides.update(self.previous_overrides)
        self.engine.dispose()

    def assert_unauthorized(self, response, detail):
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), {"detail": detail})
        self.assertEqual(response.headers["www-authenticate"], "Bearer")

    def request_token(self, token):
        return self.client.get("/private", headers={"Authorization": f"Bearer {token}"})

    def test_missing_credentials_reach_jwt_dependency(self):
        with patch.object(jwt_auth, "authentication_error", wraps=jwt_auth.authentication_error) as error:
            self.assert_unauthorized(self.client.get("/private"), "Not authenticated")
            error.assert_called_once_with("Not authenticated")

    def test_empty_or_wrong_scheme(self):
        for header in ("", "Bearer", "Bearer ", "Basic dXNlcjpwYXNz", "Token abc"):
            with self.subTest(header=header):
                response = self.client.get("/private", headers={"Authorization": header})
                self.assert_unauthorized(response, "Not authenticated")

    def test_valid_access_token(self):
        response = self.request_token(jwt_auth.generate_access_token(1))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "This is a private route."})

    def test_expired_access_token(self):
        token = jwt_auth.generate_access_token(1, expires_delta=timedelta(seconds=-1))
        self.assert_unauthorized(self.request_token(token), "Authentication failed. token expired")

    def test_refresh_token_is_rejected(self):
        self.assert_unauthorized(
            self.request_token(jwt_auth.generate_refresh_token(1)),
            "Authentication failed. token type not valid",
        )

    def test_unknown_user(self):
        self.assert_unauthorized(self.request_token(jwt_auth.generate_access_token(999)), "User not found")

    def test_malformed_token(self):
        self.assert_unauthorized(self.request_token("not-a-jwt"), "Authentication failed. Decode error")

    def test_invalid_signature(self):
        token = jwt.encode(
            {"user_id": 1, "type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
            "a-different-test-secret-key-32-bytes",
            algorithm=jwt_auth.ALGORITHM,
        )
        self.assert_unauthorized(self.request_token(token), "Authentication failed. invalid signature")

    def test_invalid_claims(self):
        payload = {"user_id": 1, "type": "access", "exp": datetime.now(timezone.utc) + timedelta(minutes=5)}
        cases = [
            ({k: v for k, v in payload.items() if k != "exp"}, "invalid token"),
            ({k: v for k, v in payload.items() if k != "user_id"}, "user id not in the payload"),
            ({k: v for k, v in payload.items() if k != "type"}, "token type not valid"),
            ({**payload, "nbf": datetime.now(timezone.utc) + timedelta(hours=1)}, "invalid token"),
        ]
        for claims, message in cases:
            with self.subTest(message=message):
                token = jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=jwt_auth.ALGORITHM)
                self.assert_unauthorized(self.request_token(token), "Authentication failed. " + message)

    def test_public_route(self):
        self.assertEqual(self.client.get("/public").status_code, 200)

    def test_registered_security_scheme(self):
        schema = app.openapi()
        self.assertEqual(schema["components"]["securitySchemes"], {"Token": {"type": "http", "scheme": "bearer"}})
        self.assertEqual(schema["paths"]["/private"]["get"]["security"], [{"Token": []}])
        for path in ("/public", "/users/login", "/users/register"):
            for operation in schema["paths"][path].values():
                self.assertNotIn("security", operation)


if __name__ == "__main__":
    unittest.main()
