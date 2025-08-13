import json
import boto3
import pg8000
import requests
from datetime import datetime
import os


def lambda_handler(event, context):
    # Get HTTP method and path
    http_method = event.get('httpMethod')
    path = event.get('path')
    
    # Database connection info
    db_host = os.environ['DB_HOST']
    db_name = os.environ['DB_NAME'] 
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    
    # Route to different handlers
    if path == '/load-stock' and http_method == 'POST':
        body = json.loads(event.get('body', '{}'))
        company_name = body.get('company_name', 'Apple')
        result = save_stock_data(company_name, db_host, db_name, db_user, db_password)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'message': result})
        }
    
    elif path == '/stocks' and http_method == 'GET':
        result = get_all_stocks(db_host, db_name, db_user, db_password)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps(result)
        }
    
    elif path == '/prices' and http_method == 'GET':
        try:
            result = get_all_prices(db_host, db_name, db_user, db_password)
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps(result)
            }
        except Exception as e:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': str(e)})
            }         
    
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }

# Your existing functions
def fetch_stock_name_data(name: str):
    url = f'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={name}&apikey=Y6M9QZP2WS432ELW'
    r = requests.get(url)
    return r.json()

def fetch_stock_price_data(name: str):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={name}&apikey=Y6M9QZP2WS432ELW'
    r = requests.get(url)
    return r.json()

def save_stock_data(name: str, db_host, db_name, db_user, db_password):
    # Get stock data (now fast!)
    name_data = fetch_stock_name_data(name)
    us_matches = [match for match in name_data['bestMatches'] if match['4. region'] == 'United States']
    if us_matches: 
        symbol = us_matches[0]['1. symbol']
        company_name = us_matches[0]['2. name']
    else:
        symbol = name_data['bestMatches'][0]['1. symbol']
        company_name = name_data['bestMatches'][0]['2. name']
    
    price_data = fetch_stock_price_data(symbol)
    
    # Database operations (also fast now)
    conn = pg8000.connect(host=db_host, database=db_name, user=db_user, password=db_password, port=5432)
    
    # Create tables
    conn.run("CREATE TABLE IF NOT EXISTS stocks (id SERIAL PRIMARY KEY, symbol VARCHAR(10) UNIQUE, name VARCHAR(255))")
    conn.run("CREATE TABLE IF NOT EXISTS stock_prices (id SERIAL PRIMARY KEY, symbol VARCHAR(10), timestamp DATE, open_price FLOAT, high_price FLOAT, low_price FLOAT, close_price FLOAT, volume INTEGER, UNIQUE(symbol, timestamp))")
    
    # Insert stock and all price data
    cursor = conn.cursor()
    cursor.execute("INSERT INTO stocks (symbol, name) VALUES (%s, %s) ON CONFLICT (symbol) DO NOTHING", (symbol, company_name))
    
    # Insert all price records
    count = 0
    for date, prices in price_data["Time Series (Daily)"].items():
        cursor.execute("INSERT INTO stock_prices (symbol, timestamp, open_price, high_price, low_price, close_price, volume) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (symbol, timestamp) DO NOTHING", 
            (symbol, datetime.strptime(date, '%Y-%m-%d'), float(prices['1. open']), float(prices['2. high']), float(prices['3. low']), float(prices['4. close']), int(prices['5. volume'])))
        count += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return f"Saved {symbol} with {count} price records to RDS!"


# New functions for GET endpoints
def get_all_stocks(db_host, db_name, db_user, db_password):
    conn = pg8000.connect(host=db_host, database=db_name, user=db_user, password=db_password, port=5432)
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol, name FROM stocks ORDER BY symbol")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    stocks = []
    for row in rows:
        stocks.append({
            'id': row[0],
            'symbol': row[1], 
            'name': row[2]
        })
    return stocks

def get_all_prices(db_host, db_name, db_user, db_password):
    conn = pg8000.connect(host=db_host, database=db_name, user=db_user, password=db_password, port=5432)
    cursor = conn.cursor()
    cursor.execute("SELECT symbol, timestamp, open_price, high_price, low_price, close_price, volume FROM stock_prices ORDER BY symbol, timestamp DESC LIMIT 100")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    prices = []
    for row in rows:
        prices.append({
            'symbol': row[0],
            'timestamp': row[1].isoformat() if row[1] else None,
            'open_price': row[2],
            'high_price': row[3],
            'low_price': row[4],
            'close_price': row[5],
            'volume': row[6]
        })
    return prices