import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.db import execute_query

def _handler(request):
    """GET /api/trades-by-symbol - Trade count by symbol"""
    query = """
        SELECT symbol, COUNT(*) AS count
        FROM trades
        GROUP BY symbol
        ORDER BY count DESC
    """
    
    results = execute_query(query)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(results)
    }
handler = make_handler(get_fn=_handler)
