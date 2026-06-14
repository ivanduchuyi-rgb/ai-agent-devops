import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
from shared.r2 import delete_file, list_files, get_new_files
from shared.constants import UPLOAD_KEY, UPLOADS_PREFIX
import json

def _auth_ok(request):
    headers = request.get("headers") or {}
    key = headers.get("x-key")
    return key == UPLOAD_KEY

def _delete(request):
    if not _auth_ok(request):
        return {"statusCode": 401, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Wrong password"})}
    path = request.get("path", "")
    parts = path.split("/")
    filename = parts[-1] if parts else ""
    if not filename:
        return {"statusCode": 400, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Missing filename"})}
    key = f"{UPLOADS_PREFIX}{filename}"
    ok = delete_file(key)
    if ok:
        return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"ok": True})}
    return {"statusCode": 404, "headers": {"Content-Type": "application/json"}, "body": json.dumps({"error": "Not found"})}

handler = make_handler(delete_fn=_delete)
