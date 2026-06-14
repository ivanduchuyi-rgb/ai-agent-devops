import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.db import execute_query

def _handler(request):
    """GET /api/profit-by-hour - P&L by hour of day"""
    query = """
        SELECT
            EXTRACT(HOUR FROM time)::int AS hour,
            COALESCE(SUM(profit::numeric), 0) AS profit,
            COUNT(*) FILTER (WHERE profit IS NOT NULL) AS closed
        FROM trades
        GROUP BY 1
        ORDER BY 1
    """
    
    results = execute_query(query)
    data = [{
        "hour": row["hour"],
        "profit": float(row["profit"]),
        "closed": row["closed"]
    } for row in results]
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }
handler = make_handler(get_fn=_handler)
