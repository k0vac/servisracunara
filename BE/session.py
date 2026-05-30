import hashlib
import hmac
import time

import config

SESSION_COOKIE = "session"
SESSION_MAX_AGE_SECONDS = 60 * 60 * 8


def _sign(payload: str) -> str:
    return hmac.new(
        config.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def create_session_token(user_id: int) -> str:
    expires_at = int(time.time()) + SESSION_MAX_AGE_SECONDS
    payload = f"{user_id}:{expires_at}"
    return f"{payload}:{_sign(payload)}"


def verify_session_token(token: str) -> int | None:
    try:
        payload, signature = token.rsplit(":", 1)
        if not hmac.compare_digest(_sign(payload), signature):
            return None

        user_id_str, expires_at_str = payload.split(":", 1)
        if int(expires_at_str) < int(time.time()):
            return None

        return int(user_id_str)
    except (ValueError, TypeError):
        return None
