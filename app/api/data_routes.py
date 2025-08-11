from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services import data_loader
from ..models import StockPrice, Stock
from ..database import get_db

router = APIRouter()

@router.post("/load-stock/{company_name}")
def put_stock(company_name: str):
    data_loader.save_stock_data(company_name)
    return {"message": "Stock data loaded successfully."}

@router.get("/prices/")
def read_prices(db: Session = Depends(get_db)):
    prices = db.query(StockPrice).all()
    return prices