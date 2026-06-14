import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.db import execute_query

def _handler(request):
    """GET /api/win-rate-by-symbol - Win rate and P&L by symbol"""
    query = """
        SELECT
            symbol,
            COUNT(*) AS total,
            COUNT(*) FILTER (WHERE profit IS NOT NULL) AS closed,
            ROUND(
                COUNT(*) FILTER (WHERE profit > 0) * 100.0
                / NULLIF(COUNT(*) FILTER (WHERE profit IS NOT NULL), 0), 1
            ) AS win_rate,
            ROUND(COALESCE(SUM(profit::numeric), 0), 2) AS total_pl
        FROM trades
        GROUP BY symbol
        ORDER BY symbol
    """
    
    results = execute_query(query)
    for row in results:
        if row['win_rate'] is not None:
            row['win_rate'] = float(row['win_rate'])
        else:
            row['win_rate'] = 0.0
        row['total_pl'] = float(row['total_pl']) if row['total_pl'] else 0.0
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(results)
    }
handler = make_handler(get_fn=_handler)
