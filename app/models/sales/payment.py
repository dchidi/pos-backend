from pydantic import BaseModel
from decimal import Decimal

class Payment(BaseModel):
    method: str  # 'cash', 'card', 'transfer', etc.
    amount: Decimal
