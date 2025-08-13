import json
import os
import logging
import boto3
from boto3.dynamodb.conditions import Key

logging.getLogger().setLevel(logging.INFO)

# ---- Config from env ----
WS_ENDPOINT = os.environ.get(
    "WS_MANAGEMENT_ENDPOINT",
    "https://050il1g34c.execute-api.us-east-2.amazonaws.com/prod"
)
SUB_TABLE = os.environ.get("SUB_TABLE", "PulseTraderSubscriptions")

# ---- AWS clients ----
apigw = boto3.client("apigatewaymanagementapi", endpoint_url=WS_ENDPOINT)
dynamodb = boto3.resource("dynamodb")
subs_table = dynamodb.Table(SUB_TABLE)
logging.info("Using DynamoDB table=%s in region=%s",
             SUB_TABLE, boto3.session.Session().region_name)


def send_message(connection_id: str, payload: dict):
    """Safe send to a single connection; never raise to API GW."""
    try:
        data = json.dumps(payload).encode("utf-8")
        apigw.post_to_connection(ConnectionId=connection_id, Data=data)
    except apigw.exceptions.GoneException:
        # Stale socket; try to remove all rows for this connection if present
        logging.info("Gone connection %s", connection_id)
    except Exception as e:
        logging.exception("post_to_connection failed: %s", e)


def handle_connect(connection_id: str):
    logging.info("CONNECT %s", connection_id)
    # Don't send during $connect; it's racy and often 410 Gone
    return {"statusCode": 200}


def handle_disconnect(connection_id: str):
    logging.info("DISCONNECT %s", connection_id)
    # Optional: clean up by connectionId if you add a GSI later
    return {"statusCode": 200}


def handle_subscribe(connection_id: str, symbol: str):
    symbol = (symbol or "AAPL").strip().upper()
    logging.info("SUBSCRIBE: table=%s region=%s cid=%s symbol=%s",
                 SUB_TABLE,
                 boto3.session.Session().region_name,
                 connection_id,
                 symbol)

    # Persist subscription (symbol, connectionId)
    try:
        resp = subs_table.put_item(Item={"symbol": symbol, "connectionId": connection_id})
        http = resp.get("ResponseMetadata", {}).get("HTTPStatusCode")
        logging.info("DDB PutItem -> HTTP %s", http)

        # sanity check: read it back
        try:
            got = subs_table.get_item(Key={"symbol": symbol, "connectionId": connection_id})
            found = "Item" in got
            logging.info("DDB GetItem found=%s", found)
        except Exception as e2:
            logging.warning("DDB GetItem check failed: %s", e2)

    except Exception as e:
        logging.exception("DynamoDB put_item failed: %s", e)

    send_message(connection_id, {
        "type": "subscribed",
        "symbol": symbol,
        "message": f"Subscribed to {symbol} price updates"
    })
    return {"statusCode": 200}


def lambda_handler(event, context):
    """
    Robust router:
    - Works for $connect/$disconnect
    - Accepts 'subscribe' or legacy 'sendmessage'
    - Falls back to $default and infers action from JSON body
    - Never throws (returns 200 even on handled errors) to avoid 502s
    """
    try:
        rc = event.get("requestContext") or {}
        route_key = rc.get("routeKey")                # e.g. '$connect', 'subscribe', '$default'
        connection_id = rc.get("connectionId")

        # Parse body (may be str or dict or empty)
        raw = event.get("body")
        if isinstance(raw, str) and raw.strip():
            try:
                body = json.loads(raw)
            except Exception:
                body = {}
        elif isinstance(raw, dict):
            body = raw
        else:
            body = {}

        action = (body.get("action") or body.get("route") or "").strip().lower()
        symbol = (body.get("symbol") or "AAPL")

        # Normalize route
        if route_key in ("$connect", "$disconnect"):
            normalized = route_key
        elif route_key in ("subscribe", "sendmessage"):
            normalized = route_key
        elif action in ("subscribe", "sendmessage"):
            normalized = action
        else:
            normalized = None

        # Dispatch
        if normalized == "$connect":
            return handle_connect(connection_id)
        if normalized == "$disconnect":
            return handle_disconnect(connection_id)
        if normalized in ("subscribe", "sendmessage"):
            return handle_subscribe(connection_id, symbol)

        # Unknown → inform client, but do not error
        logging.warning("Unknown route. routeKey=%s action=%s body=%s", route_key, action, body)
        send_message(connection_id, {"type": "error", "message": "Unknown route"})
        return {"statusCode": 200}

    except Exception as e:
        # Catch‑all so API Gateway never gets a Lambda error (which causes 502)
        logging.exception("Unhandled error: %s", e)
        try:
            rc = event.get("requestContext") or {}
            cid = rc.get("connectionId")
            if cid:
                send_message(cid, {"type": "error", "message": "Internal error"})
        except Exception:
            pass
        return {"statusCode": 200}