import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
import time

def _handler(request):
    """GET /api/system - System metrics (mock - no Prometheus)"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "cpu": None,
            "memory": None,
            "load": None,
            "uptime": {"seconds": int(time.time()), "days": 0, "hours": 0},
            "disk": None,
            "disk_data": None,
            "network": None,
            "processes": None,
            "note": "Prometheus metrics not available in serverless deployment"
        })
    }

def history_handler(request):
    """GET /api/system/history - System history (mock)"""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "cpu": {"status": "mock"},
            "memory": {"status": "mock"},
            "disk_io": {"status": "mock"},
            "note": "Prometheus metrics not available in serverless deployment"
        })
    }
handler = make_handler(get_fn=_handler)
