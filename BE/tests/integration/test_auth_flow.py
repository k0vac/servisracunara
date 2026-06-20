import pytest

from session import SESSION_COOKIE
from tests.conftest import login


@pytest.mark.integration
def test_login_me_logout_flow(seeded_client) -> None:
    client = seeded_client

    login(client)
    assert client.cookies.get(SESSION_COOKIE) is not None

    me_response = client.get("/api/auth/me")
    assert me_response.status_code == 200
    assert me_response.json()["username"] == "admin"

    logout_response = client.post("/api/auth/logout")
    assert logout_response.status_code == 200

    unauthenticated_response = client.get("/api/auth/me")
    assert unauthenticated_response.status_code == 401
