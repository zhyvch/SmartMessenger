from pydantic import BaseModel


class AskSchema(BaseModel):
    user_input: str


class AskResponseSchema(BaseModel):
    response: str
