from pydantic import BaseModel


class CreateTodo(BaseModel):
    title: str
    description: str
    status: str
