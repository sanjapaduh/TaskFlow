from typing import List

from pydantic import BaseModel, Field

from models import ColorEnum


class Tag_request(BaseModel):
    name: str
    color: ColorEnum

class Todo_request(BaseModel):
    name: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=25)
    done: bool
    importance: int = Field(ge=0, le=10)
    tags: List[Tag_request] = []

