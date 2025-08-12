import os, json, boto3, logging
logging.getLogger().setLevel(logging.INFO)

APIGW_ENDPOINT = os.environ.get(
    "WS_MANAGEMENT_ENDPOINT",
    "https://050il1g34c.execute-api.us-east-2.amazonaws.com/prod"
)
apigw = boto3.client("apigatewaymanagementapi", endpoint_url=APIGW_ENDPOINT)

def lambda_handler(event, _):
    rc = event.get("requestContext", {})
    route = rc.get("routeKey")
    cid = rc.get("connectionId")
    logging.info({"route": route, "cid": cid})

    if route == "$connect":
        _send(cid, {"type": "welcome", "message": "Connected to PulseTrader WebSocket!"})
        return {"statusCode": 200}
    if route == "$disconnect":
        # TODO: remove all subscriptions for cid
        return {"statusCode": 200}
    if route == "subscribe":
        body = json.loads(event.get("body", "{}"))
        symbol = body.get("symbol", "AAPL")
        # TODO: persist (symbol, cid) in DynamoDB
        _send(cid, {"type":"subscribed","symbol":symbol,"message":f"Subscribed to {symbol} price updates"})
        return {"statusCode": 200}
    return {"statusCode": 400, "body": f"Unknown route {route}"}

def _send(cid, msg):
    try:
        apigw.post_to_connection(ConnectionId=cid, Data=json.dumps(msg).encode("utf-8"))
    except apigw.exceptions.GoneException:
        logging.warning("Gone: %s", cid)
    except Exception:
        logging.exception("post_to_connection failed")
        raise
