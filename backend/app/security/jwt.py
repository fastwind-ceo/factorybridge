import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from app.core.config import settings


class TokenError(Exception):
    pass


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def _sign(message: str) -> str:
    digest = hmac.new(settings.secret_key.encode("utf-8"), message.encode("ascii"), hashlib.sha256).digest()
    return _b64url_encode(digest)


def encode_token(payload: dict[str, Any]) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    header_part = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_part = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_part}.{payload_part}"
    return f"{signing_input}.{_sign(signing_input)}"


def decode_token(token: str) -> dict[str, Any]:
    header_part, payload_part, signature = token.split(".")
    signing_input = f"{header_part}.{payload_part}"
    expected_signature = _sign(signing_input)
    if not hmac.compare_digest(signature, expected_signature):
        raise TokenError("Invalid token signature")
    payload = json.loads(_b64url_decode(payload_part))
    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(datetime.now(timezone.utc).timestamp()):
        raise TokenError("Token expired")
    return payload


def create_access_token(subject: str, roles: list[str]) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "roles": roles,
        "type": "access",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_access_token_expire_minutes)).timestamp()),
    }
    return encode_token(payload)
