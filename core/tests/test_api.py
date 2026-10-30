def test_login_response_401(anon_client):
    payload = {
        "username": "sinagan",
        "password": "23041385",
    }

    response = anon_client.post("/users/login", json=payload)

    assert response.status_code == 401
