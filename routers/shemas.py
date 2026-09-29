from pydantic import BaseModel, Field


class Todo_request(BaseModel):
    name: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=25)
    done: bool

    importance: int = Field(
        ge=0,
        le=10
    )
