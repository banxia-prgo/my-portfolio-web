import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
from .settings import settings

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    return password_hash.verify(password, hashed)

def new_session_token() -> str:
    return secrets.token_urlsafe(48)

def token_digest(token: str) -> str:
    return hmac.new(settings.secret_key.encode("utf-8"), token.encode("utf-8"), hashlib.sha256).hexdigest()

def session_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(hours=settings.session_ttl_hours)

def new_csrf_token() -> str:
    return secrets.token_urlsafe(32)
