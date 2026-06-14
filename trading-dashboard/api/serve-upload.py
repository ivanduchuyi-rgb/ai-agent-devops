import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.r2 import generate_presigned_get_url, file_exists, get_public_url
from shared.constants import UPLOADS_PREFIX

def _handler(request, filename: str):
    """GET /uploads/<filename> - Serve uploaded file via presigned URL redirect"""
    key = f"{UPLOADS_PREFIX}{filename}"
    
    if not file_exists(key):
        return {
            "statusCode": 404,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Not found"})
        }
    
    # Generate presigned GET URL (1 hour expiry)
    presigned_url = generate_presigned_get_url(key, expires_in=3600)
    
    # Redirect to presigned URL
    return {
        "statusCode": 302,
        "headers": {
            "Location": presigned_url,
            "Cache-Control": "public, max-age=300"
        },
        "body": ""
    }
handler = make_handler(get_fn=_handler)
