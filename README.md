# PulseTrader - Real-Time Trading Analytics Platform

A real-time financial data analytics platform built with Python, FastAPI, PostgreSQL, and WebSockets.

## Tech Stack

- **Backend**: Python, FastAPI
- **Database**: PostgreSQL (time-series optimized)
- **Real-time**: WebSockets for live price streaming
- **Caching**: Redis
- **Deployment**: Docker, AWS RDS
- **Data Source**: Alpha Vantage API

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
```

6. **Run the application**
```bash
uvicorn app.main:app --reload
```

## Features (In Development)

- [ ] Real-time stock price ingestion
- [ ] WebSocket streaming for live updates
- [ ] Complex SQL analytics with window functions
- [ ] Technical indicator calculations
- [ ] Portfolio backtesting
- [ ] Redis caching for performance
- [ ] AWS deployment

## API Endpoints

- `GET /health` - Health check
- `GET /stocks` - List all tracked stocks
- `POST /stocks` - Add new stock to tracking
- `GET /stocks/{symbol}/prices` - Get price history
- `WS /ws/prices` - Live price updates

## Project Goals

Learning advanced backend development concepts including:
- Time-series database optimization
- Real-time data pipelines
- Cloud deployment architecture
- Production-ready API design