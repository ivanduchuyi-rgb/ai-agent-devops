import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from shared.vercel import make_handler
from shared.r2 import add_to_state
from shared.constants import UPLOAD_KEY
import json

def _handler(request):
    headers = request.get("headers") or {}
    query = request.get("queryStringParameters") or {}
    key = headers.get("x-key") or query.get("key")
    if key != UPLOAD_KEY:
        return {"statusCode": 401, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Wrong password"})}
    body = request.get("body")
    if not body:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Missing body"})}
    try:
        data = json.loads(body)
    except:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Invalid JSON"})}
    filename = data.get("filename")
    if not filename:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Missing filename"})}
    add_to_state(filename)
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"ok": True, "filename": filename})}

handler = make_handler(post_fn=_handler)
