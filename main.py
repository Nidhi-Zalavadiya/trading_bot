from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bot.client import BinanceFuturesClient
from bot.orders import place_order as execute_order
from typing import Optional

app = FastAPI()

# Allow gui.html (opened directly from disk) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class OrderRequest(BaseModel):
    apiKey: str
    apiSecret: str
    symbol: str
    side: str
    type: str
    quantity: float
    price: Optional[float] = None 
    stop_price: Optional[float] = None

@app.post("/api/trade")
async def trade(req: OrderRequest):
    try:
        client = BinanceFuturesClient(req.apiKey, req.apiSecret)
        
        result = execute_order(
            client=client,
            symbol=req.symbol,
            side=req.side,
            order_type=req.type,
            quantity=req.quantity,
            price=req.price,
            stop_price=req.stop_price
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)