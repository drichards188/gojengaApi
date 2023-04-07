from decimal import *

from pydantic import BaseModel


class Portfolio(BaseModel):
    name: str
    portfolio: list[object]

