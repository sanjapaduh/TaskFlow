from typing import List

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from models import ColorEnum

class AppSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class CreateUserRequest(AppSchema):
    username: str = Field(pattern=r".*\d{1}.*")
    email: EmailStr |None = None
    password: str


class AccessToken(AppSchema):
    access_token: str
    token_type: str


class Tag_request(AppSchema):
    name: str
    color: ColorEnum


class Todo_request(AppSchema):
    name: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=25)
    done: bool
    importance: int = Field(ge=0, le=10)
    tags: List[Tag_request] = []
