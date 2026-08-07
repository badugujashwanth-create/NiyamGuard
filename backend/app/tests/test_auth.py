import pytest

from app.config import settings


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


def test_refresh_token_rotates_and_rejects_replay(client) -> None:
    login = client.post(
        "/api/auth/login",
        json={"email": "viewer@niyamguard.local", "password": "Viewer@12345"},
    )
    original = login.json()["refresh_token"]
    rotated = client.post("/api/auth/refresh", json={"refresh_token": original})
    assert rotated.status_code == 200
    assert rotated.json()["refresh_token"] != original

    replay = client.post("/api/auth/refresh", json={"refresh_token": original})
    assert replay.status_code == 401


def test_cookie_auth_mode_uses_httponly_session_and_rotates(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "auth_cookie_mode", True)
    monkeypatch.setattr(settings, "auth_cookie_secure", False)
    monkeypatch.setattr(settings, "auth_cookie_samesite", "strict")

    login = client.post(
        "/api/auth/login",
        json={"email": "viewer@niyamguard.local", "password": "Viewer@12345"},
    )
    assert login.status_code == 200
    assert login.json()["access_token"] is None
    assert login.json()["refresh_token"] is None
    assert "niyamguard_access=" in login.headers["set-cookie"]
    assert "HttpOnly" in login.headers["set-cookie"]
    assert "SameSite=strict" in login.headers["set-cookie"]

    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["user"]["email"] == "viewer@niyamguard.local"

    refresh = client.post("/api/auth/refresh", json={})
    assert refresh.status_code == 200
    assert refresh.json()["access_token"] is None
    assert refresh.json()["refresh_token"] is None

    logout = client.post("/api/auth/logout", json={})
    assert logout.status_code == 200
    assert "niyamguard_access=\"\"" in logout.headers["set-cookie"]
    assert "SameSite=strict" in logout.headers["set-cookie"]
    assert client.get("/api/auth/me").status_code == 401
