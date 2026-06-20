from unittest.mock import patch

import pytest

import session
from session import create_session_token, verify_session_token


@pytest.mark.unit
def test_verify_session_token_round_trip_and_rejects_invalid() -> None:
    with patch.object(session.time, "time", return_value=1_000_000):
        token = create_session_token(user_id=42)

    with patch.object(session.time, "time", return_value=1_000_000):
        assert verify_session_token(token) == 42

    tampered = token[:-1] + ("0" if token[-1] != "0" else "1")
    with patch.object(session.time, "time", return_value=1_000_000):
        assert verify_session_token(tampered) is None

    with patch.object(session.time, "time", return_value=1_000_000 + session.SESSION_MAX_AGE_SECONDS + 1):
        assert verify_session_token(token) is None
