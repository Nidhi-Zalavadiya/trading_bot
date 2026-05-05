# 📈 Binance Futures Testnet Trading Bot
![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green?logo=fastapi)
![Binance](https://img.shields.io/badge/Binance-Futures%20Testnet-yellow?logo=binance)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

A clean, production-structured Python CLI + Web GUI application that places futures orders on **Binance Futures Testnet (USDT-M)** with full logging, input validation, and error handling — built for the PrimeTrade.ai Python Developer application task.

---

## ✅ Requirements Checklist

| Requirement | Status | Notes |
|---|---|---|
| Place MARKET orders | ✅ | BUY & SELL, tested on testnet |
| Place LIMIT orders | ✅ | BUY & SELL with GTC time-in-force |
| CLI with argparse | ✅ | `place`, `account`, `open-orders` sub-commands |
| Symbol validation | ✅ | Alphanumeric, uppercase normalised |
| Side validation | ✅ | BUY / SELL only |
| Order type validation | ✅ | MARKET / LIMIT / STOP_MARKET |
| Quantity validation | ✅ | Must be > 0 |
| Price validation | ✅ | Required for LIMIT, ignored for MARKET |
| Order request summary printed | ✅ | Formatted table in terminal |
| Order response details printed | ✅ | orderId, status, executedQty, avgPrice |
| Success / failure message | ✅ | Coloured ANSI output |
| Structured code (client + CLI layer) | ✅ | 4-layer architecture |
| API request/response logging to file | ✅ | DEBUG level with full body |
| Exception handling (input/API/network) | ✅ | 3 distinct exception types |
| **Bonus: Third order type** | ✅ | STOP_MARKET implemented |
| **Bonus: Enhanced CLI UX** | ✅ | ANSI colours, separators, `account` + `open-orders` |
| **Bonus: Lightweight UI** | ✅ | Full HTML/JS trading dashboard (`gui.html`) |

---

## 🏗️ Project Structure

```
trading_bot/
├── bot/
│   ├── __init__.py
│   ├── client.py          # Binance REST API wrapper (HMAC signing, requests, errors)
│   ├── orders.py          # Order placement logic (validation → API → formatted result)
│   ├── validators.py      # Pure input validation — raises ValueError with clear messages
│   └── logging_config.py  # Logger factory: file (DEBUG) + console (INFO) handlers
├── logs/                  # Auto-created; daily rotating log files
│   ├── binance_client_YYYYMMDD.log
│   ├── orders_YYYYMMDD.log
│   └── cli_YYYYMMDD.log
├── gui.html               # Bonus: standalone HTML trading dashboard
├── main.py                # Bonus: FastAPI backend for gui.html
├── cli.py                 # CLI entry point (argparse sub-commands)
├── .env.example           # Template for API credentials
├── .gitignore
├── requirements.txt
└── README.md
```

### Layer Responsibilities

| Layer | File | Role |
|---|---|---|
| **CLI** | `cli.py` | Parse args, print formatted/coloured output, call order layer |
| **GUI Backend** | `main.py` | FastAPI server serving gui.html requests |
| **Orders** | `bot/orders.py` | Validate inputs, delegate to client, format result |
| **Client** | `bot/client.py` | HMAC-SHA256 sign, HTTP calls, typed exceptions |
| **Validators** | `bot/validators.py` | Pure validation functions, raise `ValueError` |
| **Logging** | `bot/logging_config.py` | Logger factory — file (DEBUG) + console (INFO) |

---

## ⚙️ Setup

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/trading_bot.git
cd trading_bot
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (CMD)
.venv\Scripts\activate.bat

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure API credentials

```bash
cp .env.example .env
```

Edit `.env` and fill in your Binance **Futures Testnet** credentials:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

> **How to get Testnet credentials:**
> 1. Go to [https://testnet.binancefuture.com](https://testnet.binancefuture.com)
> 2. Sign in with your GitHub account
> 3. Navigate to **API Management** → Generate a new key pair
> 4. Copy the API Key and Secret into your `.env` file

---

## 🚀 CLI Usage

All commands follow this format:

```
python cli.py <command> [options]
```

### Place a MARKET order

```bash
# BUY 0.001 BTC at market price
python cli.py place --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# SELL 0.01 ETH at market price
python cli.py place --symbol ETHUSDT --side SELL --type MARKET --quantity 0.01
```

### Place a LIMIT order

```bash
# SELL 0.001 BTC at 85,000 USDT (GTC)
python cli.py place --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 85000

# BUY 0.01 ETH at 3,200 USDT
python cli.py place --symbol ETHUSDT --side BUY --type LIMIT --quantity 0.01 --price 3200
```

### Place a STOP_MARKET order (Bonus — third order type)

```bash
# SELL 0.001 BTC if price drops to 60,000 (stop-loss)
python cli.py place --symbol BTCUSDT --side SELL --type STOP_MARKET --quantity 0.001 --stop-price 60000
```

### View account balances

```bash
python cli.py account
```

### List open orders

```bash
# All open orders
python cli.py open-orders

# Filtered by symbol
python cli.py open-orders --symbol BTCUSDT
```

### Help

```bash
python cli.py --help
python cli.py place --help
```

---

## 🖥️ GUI Usage (Bonus)

The bot includes a full HTML trading dashboard (`gui.html`) backed by a FastAPI server.

### Start the FastAPI backend

```bash
python main.py
# Server starts at http://127.0.0.1:8000
```

### Open the GUI

Simply open `gui.html` in your browser. Enter your Testnet API key and secret directly in the settings panel, then place orders via the visual interface.

**GUI features:**
- Live ticker prices (BTCUSDT, ETHUSDT, BNBUSDT, SOLUSDT)
- Interactive order form (MARKET / LIMIT / STOP_MARKET)
- Order book simulation
- Order history log panel
- Real-time connection status indicator

> **Note:** The GUI connects to `http://127.0.0.1:8000` — the FastAPI server must be running.

---

## 📋 Sample Terminal Output

### MARKET BUY

```
📋 Order Request
────────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : BUY
  Type       : MARKET
  Quantity   : 0.001
────────────────────────────────────────────────────────────
────────────────────────────────────────────────────────────
  ORDER SUMMARY
────────────────────────────────────────────────────────────
  Order ID        : 13096336176
  Symbol          : BTCUSDT
  Side            : BUY
  Type            : MARKET
  Status          : NEW
  Quantity        : 0.0010
  Executed Qty    : 0.0000
  Time In Force   : GTC
────────────────────────────────────────────────────────────
✅  Order placed successfully!
```

### LIMIT SELL

```
📋 Order Request
────────────────────────────────────────────────────────────
  Symbol     : BTCUSDT
  Side       : SELL
  Type       : LIMIT
  Quantity   : 0.001
  Price      : 85000.0
────────────────────────────────────────────────────────────
────────────────────────────────────────────────────────────
  ORDER SUMMARY
────────────────────────────────────────────────────────────
  Order ID        : 13096337044
  Symbol          : BTCUSDT
  Side            : SELL
  Type            : LIMIT
  Status          : NEW
  Quantity        : 0.0010
  Executed Qty    : 0.0000
  Limit Price     : 85000.00
  Time In Force   : GTC
────────────────────────────────────────────────────────────
✅  Order placed successfully!
```

### Validation Error

```
❌ Validation Error: Quantity must be greater than 0. Got: -1.0.
```

### API Error (Invalid Symbol)

```
❌ API Error: Binance API error -1121: Invalid symbol.
```

---

## 📝 Logging

Three separate log files are created daily under `logs/`:

| File | Logger | Content |
|---|---|---|
| `binance_client_YYYYMMDD.log` | `binance_client` | Raw HTTP requests, full response bodies, API errors |
| `orders_YYYYMMDD.log` | `orders` | Order requests, formatted results |
| `cli_YYYYMMDD.log` | `cli` | Validation errors, API errors, session events |

- **File handler** — DEBUG level (full request params, raw response body)
- **Console handler** — INFO level (summaries and errors only — keeps terminal clean)

Log format:
```
2026-05-01 17:04:22 | INFO     | binance_client | Order placed successfully | orderId=13096336176 status=NEW
```

Log files are **git-ignored** by default. Sample testnet logs are included in `logs/` for evaluation.

---

## 🔒 Error Handling

| Scenario | Exception | Exit Code |
|---|---|---|
| Empty or invalid symbol | `ValueError` via `validate_symbol` | 1 |
| Invalid side (not BUY/SELL) | `ValueError` via `validate_side` | 1 |
| Invalid order type | `ValueError` via `validate_order_type` | 1 |
| Negative or zero quantity | `ValueError` via `validate_quantity` | 1 |
| Missing price for LIMIT order | `ValueError` via `validate_price` | 1 |
| Missing stop price for STOP_MARKET | `ValueError` via `validate_stop_price` | 1 |
| Binance API error (e.g. -1121) | `BinanceClientError` with code + message | 1 |
| Connection timeout / DNS failure | `NetworkError` with helpful message | 1 |
| Non-JSON API response | `BinanceClientError` with raw body snippet | 1 |

---

## ✅ Assumptions

1. **Testnet only** — The base URL is hardcoded to `https://testnet.binancefuture.com`. Do not use real API keys.
2. **USDT-M Futures** — All orders target the USDT-margined perpetual futures market.
3. **`timeInForce` defaults to `GTC`** for LIMIT orders. Adjustable in `client.py` if needed.
4. **Quantity precision** — Passed as-is from the CLI. Binance rejects values that violate the symbol's `LOT_SIZE` filter. In production you would fetch `exchangeInfo` and round to the correct step size.
5. **No position management** — The bot places orders but does not track open positions or PnL beyond what the `account` command displays.
6. **`reduce_only` flag** — Supported via `--reduce-only` on the CLI, defaults to `False`.
7. **GUI credentials** — The `gui.html` dashboard accepts API credentials at runtime via an input field. They are never stored to disk.

---

## 📦 Dependencies

| Package | Purpose |
|---|---|
| `requests` | HTTP calls to Binance REST API |
| `python-dotenv` | Load `.env` credentials into environment |
| `fastapi` | Backend server for `gui.html` (bonus feature) |
| `uvicorn` | ASGI server for FastAPI |

No heavy SDK — the client uses raw REST calls with HMAC-SHA256 signing for full transparency and auditability.

---

## 🧩 Bonus Features Implemented

- ✅ **STOP_MARKET order type** — Third order type with `--stop-price` CLI argument
- ✅ **`account` sub-command** — View total balance, available balance, and unrealised PnL
- ✅ **`open-orders` sub-command** — List and filter open orders by symbol
- ✅ **Coloured ANSI terminal output** — Green for success, red for errors, cyan for headers
- ✅ **Layered architecture** — Clean CLI → Orders → Client → Validators separation
- ✅ **Full HTML trading GUI** — `gui.html` with Chart.js, order book, ticker feed, and order history

---

## 👤 Author

Built as part of the **PrimeTrade.ai Python Developer** application task.
