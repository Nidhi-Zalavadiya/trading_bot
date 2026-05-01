from __future__ import annotations

import argparse
import json
import os
import sys

from dotenv import load_dotenv

from bot.client import BinanceFuturesClient, BinanceClientError, NetworkError
from bot.logging_config import setup_logger
from bot.orders import place_order

load_dotenv()
logger = setup_logger("cli")

# ── ANSI colour helpers ──────────────────────────────────────────────────────

GREEN = "\033[92m"
RED = "\033[91m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"


def cprint(msg: str, colour: str = "") -> None:
    print(f"{colour}{msg}{RESET}")


def print_separator(char: str = "─", width: int = 60) -> None:
    print(char * width)


def print_order_result(result: dict) -> None:
    """Pretty-print order result to terminal."""
    print_separator()
    cprint("  ORDER SUMMARY", BOLD + CYAN)
    print_separator()
    fields = [
        ("Order ID",      result.get("orderId")),
        ("Symbol",        result.get("symbol")),
        ("Side",          result.get("side")),
        ("Type",          result.get("type")),
        ("Status",        result.get("status")),
        ("Quantity",      result.get("origQty")),
        ("Executed Qty",  result.get("executedQty")),
        ("Avg Price",     result.get("avgPrice")),
        ("Limit Price",   result.get("price")),
        ("Stop Price",    result.get("stopPrice")),
        ("Time In Force", result.get("timeInForce")),
    ]
    for label, value in fields:
        if value not in (None, "", "0", "0.00000000"):
            print(f"  {BOLD}{label:<16}{RESET}: {value}")
    print_separator()

def cmd_place(client: BinanceFuturesClient, args: argparse.Namespace) -> None:
    """Handle the 'place' sub-command."""
    cprint("\n📋 Order Request", BOLD + CYAN)
    print_separator()
    print(f"  Symbol     : {args.symbol}")
    print(f"  Side       : {args.side}")
    print(f"  Type       : {args.type}")
    print(f"  Quantity   : {args.quantity}")
    if args.price:
        print(f"  Price      : {args.price}")
    if args.stop_price:
        print(f"  Stop Price : {args.stop_price}")
    print_separator()

    try:
        result = place_order(
            client=client,
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price,
            stop_price=args.stop_price,
            reduce_only=args.reduce_only,
        )
    except ValueError as exc:
        cprint(f"\n❌ Validation Error: {exc}", RED)
        logger.error("Validation error: %s", exc)
        sys.exit(1)
    except BinanceClientError as exc:
        cprint(f"\n❌ API Error: {exc}", RED)
        logger.error("API error: %s", exc)
        sys.exit(1)
    except NetworkError as exc:
        cprint(f"\n❌ Network Error: {exc}", RED)
        logger.error("Network error: %s", exc)
        sys.exit(1)

    print_order_result(result)
    cprint("✅  Order placed successfully!\n", GREEN + BOLD)


def cmd_account(client: BinanceFuturesClient, _args: argparse.Namespace) -> None:
    """Handle the 'account' sub-command."""
    try:
        data = client.get_account()
    except (BinanceClientError, NetworkError) as exc:
        cprint(f"\n❌ Error: {exc}", RED)
        sys.exit(1)

    cprint("\n💰 Account Overview", BOLD + CYAN)
    print_separator()
    print(f"  Total Wallet Balance  : {data.get('totalWalletBalance')} USDT")
    print(f"  Available Balance     : {data.get('availableBalance')} USDT")
    print(f"  Total Unrealised PnL  : {data.get('totalUnrealizedProfit')} USDT")
    print_separator()
    assets = [a for a in data.get("assets", []) if float(a.get("walletBalance", 0)) != 0]
    if assets:
        cprint("  Non-zero asset balances:", YELLOW)
        for asset in assets:
            print(f"    {asset['asset']}: {asset['walletBalance']}")
    print()


def cmd_open_orders(client: BinanceFuturesClient, args: argparse.Namespace) -> None:
    """Handle the 'open-orders' sub-command."""
    try:
        orders = client.get_open_orders(symbol=args.symbol)
    except (BinanceClientError, NetworkError) as exc:
        cprint(f"\n❌ Error: {exc}", RED)
        sys.exit(1)

    if not orders:
        cprint("\nNo open orders found.\n", YELLOW)
        return

    cprint(f"\n📂 Open Orders ({len(orders)} found)", BOLD + CYAN)
    print_separator()
    for o in orders:
        print(
            f"  [{o['orderId']}] {o['symbol']} {o['side']} {o['type']} "
            f"qty={o['origQty']} price={o.get('price', 'N/A')} status={o['status']}"
        )
    print()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="trading_bot",
        description="Binance Futures Testnet Trading Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
  python cli.py place --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.01 --price 3500
  python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 60000
  python cli.py account
  python cli.py open-orders --symbol BTCUSDT
        """,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ── place ──
    place_p = sub.add_parser("place", help="Place a new futures order")
    place_p.add_argument("--symbol",      required=True,  help="Trading pair, e.g. BTCUSDT")
    place_p.add_argument("--side",        required=True,  choices=["BUY", "SELL"], help="Order side")
    place_p.add_argument("--type",        required=True,  dest="type",
                         choices=["MARKET", "LIMIT", "STOP_MARKET"], help="Order type")
    place_p.add_argument("--quantity",    required=True,  type=float, help="Order quantity in base asset")
    place_p.add_argument("--price",       required=False, type=float, default=None, help="Limit price (LIMIT orders)")
    place_p.add_argument("--stop-price",  required=False, type=float, default=None,
                         dest="stop_price", help="Stop trigger price (STOP_MARKET orders)")
    place_p.add_argument("--reduce-only", action="store_true", default=False,
                         dest="reduce_only", help="Reduce-only flag")

    # ── account ──
    sub.add_parser("account", help="Show account balances and PnL")

    # ── open-orders ──
    oo_p = sub.add_parser("open-orders", help="List open orders")
    oo_p.add_argument("--symbol", required=False, default=None, help="Filter by symbol")

    return parser


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    # Load credentials from environment (set via .env or shell)
    api_key = os.getenv("BINANCE_API_KEY", "").strip()
    api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

    if not api_key or not api_secret:
        cprint("❌ Error: BINANCE_API_KEY and BINANCE_API_SECRET must be set in your environment or .env file.", RED)
        sys.exit(1)

    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

    dispatch = {
        "place":       cmd_place,
        "account":     cmd_account,
        "open-orders": cmd_open_orders,
    }

    handler = dispatch.get(args.command)
    if handler:
        handler(client, args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
