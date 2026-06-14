import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from shared.db import get_connection

def _handler(request):
    """GET /api/csv - Export all trades as CSV"""
    query = """
        SELECT time, symbol, type, lot, open_price, close_price, profit, score, comment
        FROM trades
        ORDER BY time DESC
    """
    
    conn = None
    try:
        conn = get_connection().__enter__()
        cur = conn.cursor()
        cur.execute(query)
        
        lines = ["time,symbol,type,lot,open_price,close_price,profit,score,comment"]
        for row in cur.fetchall():
            profit_str = f"{row[6]:.2f}" if row[6] is not None else ""
            lines.append(f"{row[0]},{row[1]},{row[2]},{row[3]},{row[4]},{row[5]},{profit_str},{row[7]},{row[8]}")
        
        cur.close()
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/csv",
                "Content-Disposition": 'attachment; filename="trades.csv"'
            },
            "body": "\n".join(lines)
        }
    finally:
        if conn:
            get_connection().__exit__(None, None, None)
handler = make_handler(get_fn=_handler)
