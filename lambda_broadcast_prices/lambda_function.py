import os, json, boto3, logging, botocore
from boto3.dynamodb.conditions import Key, Attr

logging.getLogger().setLevel(logging.INFO)

WS_ENDPOINT = os.environ["WS_MANAGEMENT_ENDPOINT"]
SUB_TABLE   = os.environ["SUB_TABLE"]

apigw = boto3.client("apigatewaymanagementapi", endpoint_url=WS_ENDPOINT)
ddb   = boto3.resource("dynamodb").Table(SUB_TABLE)

def _post(cid: str, payload: dict):
    try:
        apigw.post_to_connection(ConnectionId=cid, Data=json.dumps(payload).encode("utf-8"))
        return True
    except apigw.exceptions.GoneException:
        logging.info("Gone connection %s", cid)
        return "gone"
    except Exception as e:
        logging.exception("post_to_connection failed cid=%s", cid)
        return False

def _fetch_subscribers(symbol: str):
    """
    Try the fast path (Query on partition key 'symbol').
    If the table key schema is different, fall back to a Scan (ok for small dev tables).
    """
    try:
        resp = ddb.query(KeyConditionExpression=Key("symbol").eq(symbol))
        items = resp.get("Items", [])
        logging.info("Query subscribers for %s -> %d items", symbol, len(items))
        return items
    except botocore.exceptions.ClientError as e:
        if e.response["Error"]["Code"] == "ValidationException":
            # Likely wrong key schema; do a scan as fallback (resume/dev ok)
            logging.warning("DDB Query failed (ValidationException). Falling back to Scan.")
            scan = ddb.scan(FilterExpression=Attr("symbol").eq(symbol))
            items = scan.get("Items", [])
            logging.info("Scan subscribers for %s -> %d items", symbol, len(items))
            return items
        raise

def lambda_handler(event, _):
    recs = event.get("Records", [])
    logging.info("Invocation with %d SQS records", len(recs))

    for r in recs:
        body_str = r.get("body", "")
        try:
            msg = json.loads(body_str) if body_str else {}
        except Exception:
            logging.warning("Bad JSON body: %s", body_str)
            continue

        symbol = (msg.get("symbol") or "AAPL").upper()
        price  = float(msg.get("price", 0))
        payload = {"type": "tick", "symbol": symbol, "price": price}

        subs = _fetch_subscribers(symbol)
        if not subs:
            logging.info("No subscribers for %s", symbol)
            continue

        dead_keys = []
        sent = 0
        for s in subs:
            cid = s.get("connectionId")
            if not cid:
                continue
            res = _post(cid, payload)
            if res is True:
                sent += 1
            elif res == "gone":
                # clean up stale connection
                # best-effort: only works if PK/SK == symbol/connectionId
                try:
                    ddb.delete_item(Key={"symbol": symbol, "connectionId": cid})
                except Exception:
                    pass

        logging.info("Broadcasted %s price to %d connection(s).", symbol, sent)

    return {"ok": True}