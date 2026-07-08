def test_seeded_admin_login_and_me_work(client) -> None:
    login = client.post(
        "/api/auth/login",
        json={"email": "admin@niyamguard.local", "password": "Admin@12345"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "admin@niyamguard.local"
    assert me.json()["user"]["role"] == "admin"


def test_wrong_password_fails_safely(client) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "admin@niyamguard.local", "password": "Wrong@12345"},
    )
    assert response.status_code == 401
    assert response.json()["success"] is False
    assert "password" in response.json()["error"]["message"].lower()


def test_refresh_token_returns_new_access_token(client) -> None:
    login = client.post(
        "/api/auth/login",
        json={"email": "viewer@niyamguard.local", "password": "Viewer@12345"},
    )
    refresh = client.post(
        "/api/auth/refresh",
        json={"refresh_token": login.json()["refresh_token"]},
    )
    assert refresh.status_code == 200
    assert refresh.json()["access_token"]
