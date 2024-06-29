from typing import List, Optional
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, Field, validator
from enum import Enum

app = FastAPI()

class Side(Enum):
    buy = "buy"
    sell = "sell"

# Trade model
class Trade(BaseModel):
    id: int
    user_id: int = Field(ge=0)
    currency: str = Field(max_length=5)
    side: Side = Field(Side.buy or Side.sell)
    price: float = Field(ge=0)
    amount: float = Field(ge=10)

    @validator('currency')
    def validate_currency(cls, v):
        if len(v) != 3 or not v.isalpha():
            raise ValueError('Invalid currency code')
        return v.upper()

trades = []

@app.post("/trades/", response_model=Trade)
async def create_trade(trade: Trade):
    trades.append(trade)
    return trade

@app.get("/trades/", response_model=List[Trade])
async def read_trades():
    return trades

@app.get("/trades/{trade_id}", response_model=Trade)
async def read_trade(trade_id: int = Path(..., gt=0)):
    trade = next((t for t in trades if t.id == trade_id), None)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade

@app.put("/trades/{trade_id}", response_model=Trade)
async def update_trade(trade_id: int, updated_trade: Trade):
    trade = next((t for t in trades if t.id == trade_id), None)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    trade.user_id = updated_trade.user_id
    trade.currency = updated_trade.currency
    trade.side = updated_trade.side
    trade.price = updated_trade.price
    trade.amount = updated_trade.amount
    return trade

@app.delete("/trades/{trade_id}", response_model=Trade)
async def delete_trade(trade_id: int):
    global trades
    trade = next((t for t in trades if t.id == trade_id), None)
    if trade is None:
        raise HTTPException(status_code=404, detail="Trade not found")
    trades = [t for t in trades if t.id != trade_id]
    return trade
