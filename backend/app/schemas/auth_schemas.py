from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)


class RefreshRequest(BaseModel):
    refresh_token: str


class UserResponse(BaseModel):
    id: str
    email: str
    role: str
    is_active: bool
    created_at: str
    updated_at: str


class TokenResponse(BaseModel):
    success: bool = True
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class CreateUserRequest(BaseModel):
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=8)
    role: str = Field(pattern="^(admin|reviewer|viewer|citizen)$")
    is_active: bool = True


class UpdateUserRequest(BaseModel):
    role: str | None = Field(default=None, pattern="^(admin|reviewer|viewer|citizen)$")
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)
