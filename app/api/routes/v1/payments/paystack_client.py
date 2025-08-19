from __future__ import annotations
from typing import Any, Dict, Optional
import httpx

from app.core.config import settings
from app.core.currency import Currency
from app.gateways.base import PaymentGateway


class PaystackClient(PaymentGateway):
    def __init__(self) -> None:
        self.base_url = str(settings.PAYSTACK_BASE_URL).rstrip("/")
        self.headers = {"Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}", "Content-Type": "application/json", "Accept": "application/json"}
        self.timeout = settings.HTTP_TIMEOUT_SECONDS

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.post(url, headers=self.headers, json=payload)
            data = r.json()
            if r.status_code >= 400 or not data.get("status"):
                raise RuntimeError(data.get("message") or r.text)
            return data["data"]

    async def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            r = await client.get(url, headers=self.headers)
            data = r.json()
            if r.status_code >= 400 or not data.get("status"):
                raise RuntimeError(data.get("message") or r.text)
            return data["data"]

    async def initialize_transaction(self, *, email: str, amount_minor: int, reference: str, callback_url: Optional[str], currency: Currency, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = {"email": email, "amount": amount_minor, "reference": reference, "currency": currency.value}
        if callback_url: payload["callback_url"] = callback_url
        if metadata: payload["metadata"] = metadata
        return await self._post("/transaction/initialize", payload)

    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        return await self._get(f"/transaction/verify/{reference}")

    async def create_plan(self, name: str, amount_minor: int, interval: str) -> Dict[str, Any]:
        return await self._post("/plan", {"name": name, "amount": amount_minor, "interval": interval})

    async def create_customer(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        payload = {"email": email}
        if first_name: payload["first_name"] = first_name
        if last_name: payload["last_name"] = last_name
        return await self._post("/customer", payload)

    async def create_subscription(self, customer: str, plan_code: str, authorization_code: str) -> Dict[str, Any]:
        return await self._post("/subscription", {"customer": customer, "plan": plan_code, "authorization": authorization_code})

