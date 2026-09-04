from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    username: str
    role: Literal["admin", "employee"]


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=10_000)


class ChatResponse(BaseModel):
    answer: str
    route: str | None = None
    grade: str | None = None


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    filename: str
    uploaded_by: str
    uploaded_at: datetime
    status: Literal["processing", "processed", "failed"]


class RegisterUserRequest(BaseModel):
    username: str = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8)
    role: Literal["admin", "employee"] = "employee"
