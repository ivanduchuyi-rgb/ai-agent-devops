import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json, urllib.request

def check_service(name, url, timeout=3):
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {"name": name, "status": "up", "code": r.status}
    except Exception as e:
        return {"name": name, "status": "down", "error": str(e)[:80]}

def _handler(request):
    services = [
        check_service("Vercel API", "https://api.vercel.com"),
        check_service("Supabase", "https://api.supabase.com"),
        check_service("Cloudflare R2", "https://api.cloudflare.com"),
    ]
    return {"statusCode": 200, "headers": {"Content-Type": "application/json"}, "body": json.dumps(services)}

handler = make_handler(get_fn=_handler)
