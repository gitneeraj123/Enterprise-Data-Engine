from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from auth import create_access_token, hash_password, require_admin, verify_password
from db import get_engine, get_user
from schemas import LoginRequest, RegisterUserRequest, TokenResponse

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest) -> TokenResponse:
    user = get_user(credentials.username)
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    return TokenResponse(access_token=token, role=user["role"])


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
def register_user(
    request: RegisterUserRequest,
    _: dict = Depends(require_admin),
) -> dict:
    try:
        with get_engine().begin() as connection:
            row = connection.execute(
                text("""
                    INSERT INTO app_users (username, password_hash, role)
                    VALUES (:username, :password_hash, :role)
                    RETURNING username, role
                """),
                {
                    "username": request.username,
                    "password_hash": hash_password(request.password),
                    "role": request.role,
                },
            ).mappings().one()
    except IntegrityError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists") from exc
    return dict(row)
