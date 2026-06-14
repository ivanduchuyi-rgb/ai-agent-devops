import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
from shared.r2 import generate_presigned_put_url, validate_file
from shared.constants import UPLOAD_KEY
import json

def _auth_ok(request):
    headers = request.get("headers") or {}
    query = request.get("queryStringParameters") or {}
    key = headers.get("x-key") or query.get("key")
    return key == UPLOAD_KEY

def _handler(request):
    if not _auth_ok(request):
        return {"statusCode": 401, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Wrong password"})}
    body = request.get("body")
    if not body:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Missing body"})}
    try:
        data = json.loads(body)
    except:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Invalid JSON"})}
    filename = data.get("filename")
    content_type = data.get("contentType")
    if not filename:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Missing filename"})}
    error = validate_file(filename)
    if error:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": error})}
    result = generate_presigned_put_url(filename, content_type)
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(result)}

handler = make_handler(post_fn=_handler)
