import os, json, urllib.request, boto3

ALPHA_KEY = os.environ["ALPHA_VANTAGE_KEY"]
SYMBOLS   = os.environ.get("SYMBOLS", "AAPL,MSFT").split(",")
QUEUE_URL = os.environ["TICKS_QUEUE_URL"]

sqs = boto3.client("sqs")

def lambda_handler(event, _):
    for symbol in SYMBOLS:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_KEY}"
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        price = float(data.get("Global Quote", {}).get("05. price", "0") or 0)
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({"symbol":symbol,"price":price}))
    return {"ok": True}