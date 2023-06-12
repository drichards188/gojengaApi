from decimal import *

from pydantic import BaseModel


class Portfolio(BaseModel):
    username: str
    portfolio: list[object]

