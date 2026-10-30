def test_login_response_401():
    payload = {
        "username": "sinagan",
        "password": "23041385",
    }

    response = client.post("/users/login", json=payload)

    assert response.status_code == 401
