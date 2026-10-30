def test_login_response_401(anon_client):
    payload = {
        "username": "sinagan",
        "password": "23041385",
    }

    response = anon_client.post("/users/login", json=payload)

    assert response.status_code == 401

def test_register_response_201(anon_client):
    payload = {
        "username": "sinashaygan",
        "password": "23041385",
        "password_confirm": "23041385"
    }

    response = anon_client.post("/users/register", json=payload)

    assert response.status_code == 201
