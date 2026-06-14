import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from shared.vercel import make_handler
import json
from typing import Dict, Any
from shared.db import execute_one

def _handler(request):
    """GET /api/stats - Overall trading statistics"""
    query = """
        SELECT
            COUNT(*) AS total_trades,
            COUNT(*) FILTER (WHERE profit IS NOT NULL) AS closed_trades,
            COUNT(*) FILTER (WHERE profit IS NULL) AS open_trades,
            MAX(time) AS last_trade_time,
            COALESCE(ROUND(
                COUNT(*) FILTER (WHERE profit > 0) * 100.0
                / NULLIF(COUNT(*) FILTER (WHERE profit IS NOT NULL), 0), 1
            ), 0) AS win_rate,
            COALESCE(SUM(profit::numeric), 0) AS total_pl,
            COUNT(*) FILTER (WHERE profit > 0) AS wins,
            COUNT(*) FILTER (WHERE profit < 0) AS losses,
            ROUND(COALESCE(AVG(profit::numeric) FILTER (WHERE profit > 0), 0), 2) AS avg_win,
            ROUND(COALESCE(AVG(profit::numeric) FILTER (WHERE profit < 0), 0), 2) AS avg_loss,
            COALESCE(MAX(profit), 0) AS best_trade,
            COALESCE(MIN(profit), 0) AS worst_trade
        FROM trades
    """
    
    result = execute_one(query)
    if not result:
        return {"statusCode": 200, "body": json.dumps({
            "total_trades": 0, "closed_trades": 0, "open_trades": 0,
            "win_rate": 0, "total_pl": 0, "wins": 0, "losses": 0,
            "avg_win": 0, "avg_loss": 0, "best_trade": 0, "worst_trade": 0,
            "profit_factor": 0, "last_trade_time": None
        })}
    
    # Convert Decimal to float
    for key in ['total_pl', 'win_rate', 'avg_win', 'avg_loss', 'best_trade', 'worst_trade']:
        if result[key] is not None:
            result[key] = float(result[key])
        else:
            result[key] = 0.0
    
    if result['last_trade_time']:
        result['last_trade_time'] = result['last_trade_time'].isoformat()
    
    # Calculate profit factor
    if result['avg_loss'] != 0:
        result['profit_factor'] = round(abs(result['avg_win'] / result['avg_loss']), 2)
    else:
        result['profit_factor'] = 0.0
    
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }
handler = make_handler(get_fn=_handler)
