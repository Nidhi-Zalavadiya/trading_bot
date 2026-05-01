from __future__ import annotations

from typing import Any

from bot.client import BinanceFuturesClient
from bot.logging_config import setup_logger
from bot.validators import (
    validate_order_type,
    validate_price,
    validate_quantity,
    validate_side,
    validate_stop_price,
    validate_symbol,
)

logger = setup_logger("orders")


def _format_order_result(response: dict) -> dict[str, Any]:
    """Pull out only the fields we actually care about from the raw Binance response."""
    return {
        "orderId": response.get("orderId"),
        "symbol": response.get("symbol"),
        "side": response.get("side"),
        "type": response.get("type"),
        "status": response.get("status"),
        "origQty": response.get("origQty"),
        "executedQty": response.get("executedQty"),
        "avgPrice": response.get("avgPrice"),
        "price": response.get("price"),
        "stopPrice": response.get("stopPrice"),
        "timeInForce": response.get("timeInForce"),
        "updateTime": response.get("updateTime"),
    }


def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float | str,
    price: float | str | None = None,
    stop_price: float | str | None = None,
    reduce_only: bool = False,
) -> dict[str, Any]:
    """Validate inputs, place the order, return a clean result dict."""

    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    price = validate_price(price, order_type)
    stop_price = validate_stop_price(stop_price, order_type)

    logger.info(
        "Order request | symbol=%s side=%s type=%s qty=%s price=%s stopPrice=%s",
        symbol, side, order_type, quantity, price, stop_price,
    )

    # --- Place ---
    raw = client.place_order(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
        stop_price=stop_price,
        reduce_only=reduce_only,
    )

    result = _format_order_result(raw)
    logger.debug("Formatted result: %s", result)
    return result
