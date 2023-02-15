from decimal import *

from pydantic import BaseModel


class Transaction(BaseModel):
    sender: str
    receiver: str
    amount: Decimal

