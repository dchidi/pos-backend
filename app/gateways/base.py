from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from app.constants import Currency


class PaymentGateway(ABC):
  @abstractmethod
  async def initialize_transaction(
    self, *, email: str, amount_minor: int, reference: str, 
    callback_url: Optional[str], currency: Currency, 
    metadata: Optional[Dict[str, Any]] = None
  ) -> Dict[str, Any]: ...


  @abstractmethod
  async def verify_transaction(self, reference: str) -> Dict[str, Any]: ...


  @abstractmethod
  async def create_plan(self, name: str, amount_minor: int, interval: str) -> Dict[str, Any]: ...


  @abstractmethod
  async def create_customer(
    self, email: str, first_name: Optional[str] = None, 
    last_name: Optional[str] = None
  ) -> Dict[str, Any]: ...


  @abstractmethod
  async def create_subscription(self, customer: str, plan_code: str, authorization_code: str) -> Dict[str, Any]: ...

