import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.r2 import list_files, get_state, get_new_files

def _handler(request):
    """GET /api/uploads - List all uploaded files"""
    files = list_files()
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(files)
    }

def new_handler(request):
    """GET /api/uploads/new - Get files not in state"""
    new_files = get_new_files()
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(new_files)
    }
handler = make_handler(get_fn=_handler)
