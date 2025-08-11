from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import engine, get_db, Base
from .models import Stock
from .api.data_routes import router as data_router

app = FastAPI()

app.include_router(data_router)

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)

@app.get("/stocks/")
def read_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    return stocks