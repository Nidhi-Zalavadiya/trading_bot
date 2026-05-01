from __future__ import annotations

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT", "STOP_MARKET"}


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalise a trading symbol.

    Rules:
    - Must be a non-empty string.
    - Converted to uppercase.
    - Only alphanumeric characters allowed.
    """
    symbol = symbol.strip().upper()
    if not symbol:
        raise ValueError("Symbol cannot be empty.")
    if not symbol.isalnum():
        raise ValueError(f"Symbol '{symbol}' contains invalid characters. Use alphanumeric only (e.g. BTCUSDT).")
    return symbol


def validate_side(side: str) -> str:
    """Validate order side — must be BUY or SELL (case-insensitive)."""
    side = side.strip().upper()
    if side not in VALID_SIDES:
        raise ValueError(f"Invalid side '{side}'. Must be one of: {', '.join(sorted(VALID_SIDES))}.")
    return side


def validate_order_type(order_type: str) -> str:
    """Validate order type — MARKET, LIMIT, or STOP_MARKET (case-insensitive)."""
    order_type = order_type.strip().upper()
    if order_type not in VALID_ORDER_TYPES:
        raise ValueError(
            f"Invalid order type '{order_type}'. Must be one of: {', '.join(sorted(VALID_ORDER_TYPES))}."
        )
    return order_type


def validate_quantity(quantity: str | float) -> float:
    """
    Validate order quantity.

    Rules:
    - Must be a positive number.
    - Must be > 0.
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Quantity '{quantity}' is not a valid number.")
    if qty <= 0:
        raise ValueError(f"Quantity must be greater than 0. Got: {qty}.")
    return qty


def validate_price(price: str | float | None, order_type: str) -> float | None:
    """
    Validate price field.

    Rules:
    - Required for LIMIT and STOP_MARKET orders.
    - Must be a positive number when provided.
    - Should be None / omitted for MARKET orders.
    """
    if order_type == "MARKET":
        if price is not None:
            # Silently ignore price for MARKET orders — common user mistake
            return None
        return None

    # LIMIT / STOP_MARKET require a price
    if price is None:
        raise ValueError(f"Price is required for {order_type} orders.")

    try:
        p = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Price '{price}' is not a valid number.")

    if p <= 0:
        raise ValueError(f"Price must be greater than 0. Got: {p}.")

    return p


def validate_stop_price(stop_price: str | float | None, order_type: str) -> float | None:
    """Validate stop price — required for STOP_MARKET orders."""
    if order_type != "STOP_MARKET":
        return None

    if stop_price is None:
        raise ValueError("Stop price (--stop-price) is required for STOP_MARKET orders.")

    try:
        sp = float(stop_price)
    except (ValueError, TypeError):
        raise ValueError(f"Stop price '{stop_price}' is not a valid number.")

    if sp <= 0:
        raise ValueError(f"Stop price must be greater than 0. Got: {sp}.")

    return sp
