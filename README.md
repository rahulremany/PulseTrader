# PulseTrader - Real-Time Trading Analytics Platform

A serverless financial data analytics platform for real-time market data ingestion, analysis, and algorithmic trading signal generation.
Built with AWS Lambda, API Gateway WebSockets, PostgreSQL (RDS), Redis (ElastiCache), and FastAPI for sub-second latency analytics.

## Tech Stack

- **Backend**: Python, FastAPI, AWS Lambda (serverless functions)
- **Database**: AWS RDS PostgreSQL (time-series optimized)
- **Real-time**: API Gateway WebSockets for live price streaming
- **Message Queue**: AWS SQS for event-driven processing
- **Caching**: AWS ElastiCache (Redis)
- **Data Source**: Alpha Vantage API
- **Deployment**: AWS Cloud (serverless architecture), Docker for local testing

## Setup

1. **Clone and navigate to project**
```bash
git clone <your-repo-url>
cd PulseTrader
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Start PostgreSQL**
```bash
docker-compose up -d
```

5. **Set up environment variables**
Create `.env` file:
```
DATABASE_URL=postgresql://trader:your_password@localhost:5432/trading_db
ALPHA_VANTAGE_API_KEY=your_api_key_here
AWS_REGION=us-east-2
```

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

## Core Features

- [ ] Real-time Stock Price Ingestion (via AWS Lambda + Alpha Vantage API)
- [ ] WebSocket Streaming for sub-second market updates
- [ ] Optimized PostgreSQL Time-Series Storage for historical data
- [ ] Analytical SQL Queries with window functions & CTEs
- [ ] Technical Indicator Calculations (EMA, RSI, Bollinger Bands, etc.)
- [ ] Portfolio Backtesting Engine with multi-timeframe support
- [ ] AWS ElastiCache Redis Caching for low-latency queries
- [ ] Fully Serverless Event-Driven Microservices Architecture

## API Endpoints

REST API (AWS Lambda via API Gateway)
- `POST /load-stock` - Health check
- `GET /stocks` - List all tracked stocks
- `GET /prices` - Get recent price data

WebSocket (Real-time feed):
- Connect to wss://<api-gateway-url>
- Send: {"action": "subscribe", "symbol": "AAPL"}
- Receive: {"symbol": "AAPL", "price": 215.32, "timestamp": "2025-08-12T14:35:00Z"}

## Architecture Overview

- **Data Ingestion**: Lambda functions fetch data from Alpha Vantage and push updates into RDS + Redis
- **Real-time Feed**: API Gateway WebSockets broadcast updates to connected clients
- **Data Processing**: Event-driven pipelines (via SQS) trigger analytical calculations
- **Storage**: Optimized PostgreSQL schema with indexed time-series tables
- **Caching**: Redis stores recent data for millisecond retrieval

## Project Goals

- Demonstrate AWS serverless architecture for real-time financial operations
- Showcase event-driven microsfervices for low latency analytics
- Build production-style cloud backend
- Practice database optimization for time-series workloads