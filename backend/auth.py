"""JWT authentication and role-based access dependencies."""

import os
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from fastapi import HTTPException, Request, status
from jose import JWTError, jwt
from passlib.context import CryptContext

from db import get_user

load_dotenv()

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "access_token")
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY must be configured.")
    return secret


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return jwt.encode(payload, _jwt_secret(), algorithm=ALGORITHM)


def get_auth_cookie_options() -> dict[str, str | bool]:
    """Return validated cookie settings shared by login and logout."""
    secure = os.getenv("COOKIE_SECURE", "true").lower() in {"1", "true", "yes"}
    same_site = os.getenv("COOKIE_SAMESITE", "lax").lower()
    if same_site not in {"lax", "strict", "none"}:
        raise RuntimeError("COOKIE_SAMESITE must be lax, strict, or none.")
    if same_site == "none" and not secure:
        raise RuntimeError("COOKIE_SECURE must be enabled when COOKIE_SAMESITE is none.")
    return {"httponly": True, "secure": secure, "samesite": same_site, "path": "/"}


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=[ALGORITHM])
        if not payload.get("sub") or not payload.get("role"):
            raise JWTError("Token payload is incomplete")
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def get_current_user(request: Request) -> dict:
    token = request.cookies.get(AUTH_COOKIE_NAME)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )
    payload = decode_access_token(token)
    user = get_user(payload["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return {"username": user["username"], "role": user["role"]}


def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    if current_user["role"] != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return current_user
