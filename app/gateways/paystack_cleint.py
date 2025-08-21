from __future__ import annotations
from typing import Any, Dict, Optional
import httpx

from app.core.settings import settings
from app.constants import Currency
from app.gateways.base import PaymentGateway


class PaystackClient(PaymentGateway):
    def __init__(self) -> None:
        self.base_url = str(settings.PAYSTACK_BASE_URL).rstrip("/")  # e.g. https://api.paystack.co
        self.headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.timeout = httpx.Timeout(
            timeout=settings.HTTP_TIMEOUT_SECONDS,  # or explicit: connect=5, read=15, write=15, pool=5
        )
        self.limits = httpx.Limits(max_keepalive_connections=100, max_connections=300)

    async def _request(self, method: str, path: str, *, json_payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout,
            limits=self.limits,
            http2=True,
            follow_redirects=True,
        ) as client:
            resp = await client.request(method, path, json=json_payload)

        req_id = resp.headers.get("x-paystack-request-id")
        ct = resp.headers.get("content-type", "")

        # Raise HTTP errors first
        try:
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            snippet = (resp.text or "")[:600]
            raise RuntimeError(f"Paystack HTTP {resp.status_code} (req {req_id}, {ct}): {snippet}") from e

        # Parse JSON safely
        try:
            body = resp.json()
        except ValueError as e:
            snippet = (resp.text or "")[:600]
            raise RuntimeError(f"Non-JSON response from Paystack (req {req_id}, {ct}): {snippet}") from e

        if not body.get("status"):
            # Paystack error envelope
            raise RuntimeError(f"Paystack error (req {req_id}): {body.get('message') or body}")

        data = body.get("data")
        if data is None:
            raise RuntimeError(f"Unexpected Paystack payload (req {req_id}): missing 'data'")
        return data

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._request("POST", path, json_payload=payload)

    async def _get(self, path: str) -> Dict[str, Any]:
        return await self._request("GET", path)

    async def initialize_transaction(
        self,
        *,
        email: str,
        amount_minor: int,
        reference: str,
        callback_url: Optional[str],
        currency: Currency,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not isinstance(amount_minor, int) or amount_minor <= 0:
            raise ValueError("amount_minor must be a positive integer in minor units")
        payload: Dict[str, Any] = {
            "email": email,
            "amount": amount_minor,
            "reference": reference,
            "currency": currency.value,
            "channels": ["card", "qr"],  # e.g. ["card","bank_transfer","ussd","qr"]
        }
        if callback_url:
            payload["callback_url"] = callback_url
        if metadata:
            payload["metadata"] = metadata
        return await self._post("/transaction/initialize", payload)

    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        return await self._get(f"/transaction/verify/{reference}")

    async def create_plan(self, name: str, amount_minor: int, interval: str) -> Dict[str, Any]:
        return await self._post("/plan", {"name": name, "amount": amount_minor, "interval": interval})

    async def create_customer(self, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None) -> Dict[str, Any]:
        payload: Dict[str, Any] = {"email": email}
        if first_name:
            payload["first_name"] = first_name
        if last_name:
            payload["last_name"] = last_name
        return await self._post("/customer", payload)

    async def create_subscription(self, customer: str, plan_code: str, authorization_code: str) -> Dict[str, Any]:
        return await self._post(
            "/subscription",
            {"customer": customer, "plan": plan_code, "authorization": authorization_code},
        )
