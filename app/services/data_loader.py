import requests
from ..models import Stock, StockPrice
from ..database import SessionLocal
from datetime import datetime

def fetch_stock_price_data(name: str):
    """
    Fetch stock data from Alpha Vantage API.
    """

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={name}&interval=5min&apikey=Y6M9QZP2WS432ELW'
    r = requests.get(url)
    return r.json()

def fetch_stock_name_data(name: str):
    """
    Fetch stock name data from Alpha Vantage API.
    """

    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={name}&apikey=Y6M9QZP2WS432ELW'
    r = requests.get(url)
    return r.json()

def save_stock_data(name: str):
    """
    Save a stock's data to the name and prices tables.
    """
    
    name_data = fetch_stock_name_data(name)
    us_matches = [match for match in name_data['bestMatches'] if match['4. region'] == 'United States']
    if us_matches: 
        symbol = us_matches[0]['1. symbol']
        company_name = us_matches[0]['2. name']
    else:
        symbol = name_data['bestMatches'][0]['1. symbol']
        company_name = name_data['bestMatches'][0]['2. name']
    
    price_data = fetch_stock_price_data(symbol)
    price_records = []
    for date, prices in price_data["Time Series (Daily)"].items():
        price_record = StockPrice(
            symbol = symbol,
            timestamp = datetime.strptime(date, '%Y-%m-%d'),
            open_price = float(prices['1. open']),
            high_price = float(prices['2. high']),
            low_price = float(prices['3. low']),
            close_price = float(prices['4. close']),
            volume = int(prices['5. volume']),
        )
        price_records.append(price_record)

    with SessionLocal() as db:
        existing_stock = db.query(Stock).filter(Stock.symbol == symbol).first()
        if not existing_stock:
            new_stock = Stock(symbol=symbol, name=company_name)
            db.add(new_stock)
        
        existing_prices = db.query(StockPrice).filter(StockPrice.symbol == symbol).count()
        if existing_prices == 0:
            db.add_all(price_records)

        db.commit()

    print("Stock data saved successfully.")

