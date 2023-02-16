from decimal import *

from pydantic import BaseModel


class Account(BaseModel):
    name: str
    balance: Decimal

