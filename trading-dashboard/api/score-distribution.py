import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.db import execute_query

def _handler(request):
    """GET /api/score-distribution - Score histogram"""
    query = """
        SELECT
            (score / 10 * 10) AS bucket,
            COUNT(*) AS count
        FROM trades
        WHERE score IS NOT NULL
        GROUP BY 1
        ORDER BY 1
    """
    
    results = execute_query(query)
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(results)
    }
handler = make_handler(get_fn=_handler)
