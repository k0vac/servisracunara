from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1)


class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    must_change_password: bool

    model_config = {"from_attributes": True}


class LoginResponse(BaseModel):
    user: UserResponse
    notifications: list[str] = []
