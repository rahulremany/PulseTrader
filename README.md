# PulseTrader

**PulseTrader** is a real-time stock price broadcasting platform built entirely on AWS serverless infrastructure.  
It demonstrates scalable WebSocket communication, event-driven data processing, and DynamoDB-backed subscriptions — all without managing servers.

---

## 🚀 Features
- **Live WebSocket Connections** — Clients connect via API Gateway WebSocket API for real-time updates.
- **Symbol Subscriptions** — Users can subscribe to one or more stock tickers and receive instant price changes.
- **Price Broadcasting** — Incoming price updates are broadcast to all subscribed clients via AWS Lambda.
- **Fully Serverless** — Built with AWS Lambda, API Gateway, DynamoDB, and SQS for maximum scalability.
- **On-Demand Pricing** — Cost-optimized using AWS on-demand services, no always-on compute required.

---

## 🛠 Architecture

1. **API Gateway (WebSocket API)**  
   - Handles client connections (`$connect`, `$disconnect`) and routes subscription actions to Lambda.

2. **Lambda Functions**  
   - **Connection Handler** — Registers new WebSocket clients and manages subscriptions.  
   - **Disconnection Handler** — Cleans up stale connections.  
   - **Broadcast Handler** — Reads price updates from SQS and pushes them to subscribers.  
   - **Price Update Ingestor** — Receives new price ticks and pushes them into the broadcast pipeline.

3. **DynamoDB**  
   - Stores active subscriptions keyed by `symbol` and `connectionId`.

4. **SQS**  
   - Decouples price ingestion from broadcasting to ensure reliability under load.

---

## 📂 Repository Structure
```
.
├── lambdas/
│   ├── connection_handler.py
│   ├── disconnection_handler.py
│   ├── subscribe_handler.py
│   ├── broadcast_handler.py
├── infrastructure/
│   ├── template.yaml          # AWS SAM / CloudFormation template
│   ├── policies/              # IAM role policies
├── requirements.txt
├── README.md
```

---

## ⚙️ Requirements
- Python 3.9+
- AWS CLI configured with permissions for:
  - API Gateway WebSocket API
  - Lambda
  - DynamoDB
  - SQS
- AWS SAM CLI (for local testing)

---

## 📦 Installation & Deployment

**Deploy with AWS SAM:**
```bash
sam build
sam deploy --guided
```

**Manual Deployment:**
1. Create DynamoDB table (`PulseTraderSubscriptions`)
2. Create SQS queue for price events
3. Deploy Lambda functions & API Gateway routes
4. Set environment variables:
    - `SUB_TABLE` = DynamoDB table name
    - `WS_MANAGEMENT_ENDPOINT` = API Gateway WebSocket management endpoint
5. Grant IAM permissions for Lambda to access DynamoDB, SQS, and API Gateway Management API

---

## 🧪 Testing
- Connect via WebSocket client to your API Gateway WebSocket URL.
- Send:
```json
{ "action": "subscribe", "symbol": "AAPL" }
```
- Publish a message to SQS:
```json
{ "symbol": "AAPL", "price": 189.45 }
```
- Observe broadcast message received by subscribed client.

---

## 📜 License
MIT License
