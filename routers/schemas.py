from pydantic import BaseModel, Field, EmailStr


class CreateUserRequest(BaseModel):
    username: str = Field(pattern=r".*\d{1}.*")
    email: EmailStr |None = None
    password: str


class AccessToken(BaseModel):
    access_token: str
    token_type: str
