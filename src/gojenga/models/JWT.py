from pydantic import BaseModel


class JWT(BaseModel):
    token: str
