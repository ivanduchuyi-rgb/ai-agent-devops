import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from typing import Optional
from shared.db import execute_query

def _handler(request):
    """GET /api/recent-trades - Paginated recent trades with optional symbol filter"""
    query_params = request.get("queryStringParameters") or {}
    
    symbol = query_params.get("symbol", "")
    limit = min(int(query_params.get("limit", 50)), 200)
    offset = int(query_params.get("offset", 0))
    
    if symbol:
        query = """
            SELECT time, symbol, type, lot, open_price, close_price, profit, score, comment
            FROM trades
            WHERE symbol = %s
            ORDER BY time DESC
            LIMIT %s OFFSET %s
        """
        params = (symbol, limit, offset)
    else:
        query = """
            SELECT time, symbol, type, lot, open_price, close_price, profit, score, comment
            FROM trades
            ORDER BY time DESC
            LIMIT %s OFFSET %s
        """
        params = (limit, offset)
    
    from shared.db import execute_query as eq
    results = eq(query, params)
    
    data = []
    for row in results:
        data.append({
            "time": row["time"].isoformat() if row["time"] else None,
            "symbol": row["symbol"],
            "type": row["type"],
            "lot": float(row["lot"]) if row["lot"] is not None else None,
            "open_price": float(row["open_price"]) if row["open_price"] is not None else None,
            "close_price": float(row["close_price"]) if row["close_price"] is not None else None,
            "profit": float(row["profit"]) if row["profit"] is not None else None,
            "score": row["score"],
            "comment": row["comment"],
        })
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(data)
    }
handler = make_handler(get_fn=_handler)
