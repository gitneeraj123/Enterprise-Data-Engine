from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from auth import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    AUTH_COOKIE_NAME,
    create_access_token,
    get_auth_cookie_options,
    get_current_user,
    hash_password,
    require_admin,
    verify_password,
)
from db import get_engine, get_user
from schemas import LoginRequest, RegisterUserRequest, UserResponse

router = APIRouter(tags=["authentication"])


@router.post("/login", response_model=UserResponse)
def login(credentials: LoginRequest, response: Response) -> UserResponse:
    user = get_user(credentials.username)
    if not user or not verify_password(credentials.password, user["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")
    token = create_access_token({"sub": user["username"], "role": user["role"]})
    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=token,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **get_auth_cookie_options(),
    )
    return UserResponse(username=user["username"], role=user["role"])


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)) -> UserResponse:
    return UserResponse(**current_user)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> Response:
    response.delete_cookie(key=AUTH_COOKIE_NAME, path="/")
    return response

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
