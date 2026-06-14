import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.db import execute_query

def _handler(request):
    """GET /api/cumulative-profit - Cumulative P&L over time"""
    query = """
        WITH hourly AS (
            SELECT
                date_trunc('hour', time) AS bucket,
                COALESCE(SUM(profit::numeric), 0) AS profit
            FROM trades
            WHERE profit IS NOT NULL
            GROUP BY 1
            ORDER BY 1
        )
        SELECT
            bucket::text,
            profit,
            SUM(profit) OVER (ORDER BY bucket) AS cumulative
        FROM hourly
        ORDER BY bucket
    """
    
    results = execute_query(query)
    data = [{
        "time": row["bucket"],
        "profit": float(row["profit"]),
        "cumulative": float(row["cumulative"])
    } for row in results]
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }
handler = make_handler(get_fn=_handler)
