from pydantic import BaseModel


class Account(BaseModel):
    name: str
    balance: float | None = None