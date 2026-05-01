from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any
from urllib.parse import urlencode

import requests

from bot.logging_config import setup_logger

# Testnet only — swap this for live URL when going to production
BASE_URL = "https://testnet.binancefuture.com"

logger = setup_logger("binance_client")


class BinanceClientError(Exception):
    """Binance returned an API-level error (bad symbol, insufficient margin, etc.)"""


class NetworkError(Exception):
    """Connection or timeout failure reaching Binance."""


class BinanceFuturesClient:
    def __init__(self, api_key: str, api_secret: str, base_url: str = BASE_URL) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "X-MBX-APIKEY": self.api_key,
                "Content-Type": "application/x-www-form-urlencoded",
            }
        )

    def _sign(self, params: dict) -> dict:
        """Binance requires every signed request to include a timestamp + HMAC-SHA256 signature."""
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        signed: bool = True,
    ) -> Any:
        params = params or {}
        if signed:
            params = self._sign(params)

        url = f"{self.base_url}{endpoint}"
        logger.debug("→ %s %s | params: %s", method.upper(), url, {k: v for k, v in params.items() if k != "signature"})

        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=10)
            elif method.upper() == "POST":
                response = self.session.post(url, data=params, timeout=10)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=10)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        except requests.exceptions.ConnectionError as exc:
            logger.error("Network connection error: %s", exc)
            raise NetworkError(f"Cannot reach Binance Testnet ({self.base_url}). Check your internet connection.") from exc
        except requests.exceptions.Timeout as exc:
            logger.error("Request timed out: %s", exc)
            raise NetworkError("Request to Binance Testnet timed out after 10 seconds.") from exc

        logger.debug("← HTTP %s | body: %s", response.status_code, response.text[:500])

        try:
            data = response.json()
        except ValueError:
            raise BinanceClientError(f"Non-JSON response (HTTP {response.status_code}): {response.text[:200]}")

        # Binance signals errors with a negative 'code' field even on HTTP 200
        if isinstance(data, dict) and "code" in data and int(data["code"]) < 0:
            msg = data.get("msg", "Unknown API error")
            logger.error("Binance API error | code=%s | msg=%s", data["code"], msg)
            raise BinanceClientError(f"Binance API error {data['code']}: {msg}")

        if not response.ok:
            raise BinanceClientError(f"HTTP {response.status_code}: {response.text[:200]}")

        return data

    def get_exchange_info(self) -> dict:
        """Symbol metadata — filters, precision, tick size. Useful for rounding qty/price correctly."""
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)

    def get_account(self) -> dict:
        """Fetch futures account details (balances, positions)."""
        return self._request("GET", "/fapi/v2/account")

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float | None = None,
        stop_price: float | None = None,
        time_in_force: str = "GTC",
        reduce_only: bool = False,
    ) -> dict:
        params: dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }

        if order_type == "LIMIT":
            if price is None:
                raise ValueError("Price must be provided for LIMIT orders.")
            params["price"] = price
            params["timeInForce"] = time_in_force

        if order_type == "STOP_MARKET":
            if stop_price is None:
                raise ValueError("Stop price must be provided for STOP_MARKET orders.")
            params["stopPrice"] = stop_price

        if reduce_only:
            params["reduceOnly"] = "true"

        logger.info(
            "Placing %s %s order | symbol=%s qty=%s price=%s stopPrice=%s",
            side,
            order_type,
            symbol,
            quantity,
            price,
            stop_price,
        )

        response = self._request("POST", "/fapi/v1/order", params=params)
        logger.info(
            "Order placed successfully | orderId=%s status=%s",
            response.get("orderId"),
            response.get("status"),
        )
        return response

    def cancel_order(self, symbol: str, order_id: int) -> dict:
        """Cancel an open order by orderId."""
        params = {"symbol": symbol, "orderId": order_id}
        return self._request("DELETE", "/fapi/v1/order", params=params)

    def get_open_orders(self, symbol: str | None = None) -> list:
        """Fetch all open orders, optionally filtered by symbol."""
        params = {}
        if symbol:
            params["symbol"] = symbol
        return self._request("GET", "/fapi/v1/openOrders", params=params)
