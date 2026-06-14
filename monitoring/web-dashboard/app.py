import os, json, time, socket as sock_mod
from datetime import datetime
from flask import Flask, jsonify, render_template, request, send_from_directory, abort
import psycopg2
import psycopg2.extras
import urllib.request

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 300

DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'host.docker.internal'),
    'port': int(os.environ.get('DB_PORT', 5432)),
    'database': os.environ.get('DB_NAME', 'trade_logs'),
    'user': os.environ.get('DB_USER', 'bot'),
    'password': os.environ.get('DB_PASS', 'NUOCh2o#mC2#'),
}

PASSWORD = 'NUOCh2o#mC2#'
UPLOAD_DIR = '/app/screenshots'
ALLOWED_EXTS = {'.png', '.jpg', '.jpeg', '.gif'}
MAX_SIZE = 10 * 1024 * 1024
STATE_FILE = '/opt/ai-agent/state/.upload_state.json'
PROM_URL = 'http://prometheus:9090'
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def query_prometheus(query):
    try:
        url = f'{PROM_URL}/api/v1/query?query={urllib.request.quote(query)}'
        with urllib.request.urlopen(url, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

# ─── Trading API ────────────────────────────────────────────

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT
            COUNT(*) AS total_trades,
            COUNT(*) FILTER (WHERE profit IS NOT NULL) AS closed_trades,
            COUNT(*) FILTER (WHERE profit IS NULL) AS open_trades,
            MAX(time) AS last_trade_time,
            COALESCE(ROUND(COUNT(*) FILTER (WHERE profit > 0) * 100.0
                / NULLIF(COUNT(*) FILTER (WHERE profit IS NOT NULL), 0), 1), 0) AS win_rate,
            COALESCE(SUM(profit::numeric), 0) AS total_pl,
            COUNT(*) FILTER (WHERE profit > 0) AS wins,
            COUNT(*) FILTER (WHERE profit < 0) AS losses,
            ROUND(COALESCE(AVG(profit::numeric) FILTER (WHERE profit > 0), 0), 2) AS avg_win,
            ROUND(COALESCE(AVG(profit::numeric) FILTER (WHERE profit < 0), 0), 2) AS avg_loss,
            COALESCE(MAX(profit), 0) AS best_trade,
            COALESCE(MIN(profit), 0) AS worst_trade
        FROM trades
    """)
    data = dict(cur.fetchone())
    for k in ('total_pl', 'win_rate', 'avg_win', 'avg_loss', 'best_trade', 'worst_trade'):
        data[k] = float(data[k]) if data[k] is not None else 0.0
    if data['last_trade_time']:
        data['last_trade_time'] = data['last_trade_time'].isoformat()
    profit_factor = abs(data['avg_win'] / data['avg_loss']) if data['avg_loss'] != 0 else 0
    data['profit_factor'] = round(profit_factor, 2)
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/trades-by-symbol')
def api_trades_by_symbol():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("SELECT symbol, COUNT(*) AS count FROM trades GROUP BY symbol ORDER BY count DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/win-rate-by-symbol')
def api_win_rate_by_symbol():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT symbol, COUNT(*) AS total,
            COUNT(*) FILTER (WHERE profit IS NOT NULL) AS closed,
            ROUND(COUNT(*) FILTER (WHERE profit > 0) * 100.0
                / NULLIF(COUNT(*) FILTER (WHERE profit IS NOT NULL), 0), 1) AS win_rate,
            ROUND(COALESCE(SUM(profit::numeric), 0), 2) AS total_pl
        FROM trades GROUP BY symbol ORDER BY symbol
    """)
    data = cur.fetchall()
    for r in data:
        r['win_rate'] = float(r['win_rate']) if r['win_rate'] is not None else 0.0
        r['total_pl'] = float(r['total_pl'])
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/profit-over-time')
def api_profit_over_time():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT date_trunc('hour', time) AS bucket,
            COALESCE(SUM(profit::numeric), 0) AS profit,
            COUNT(*) FILTER (WHERE profit IS NOT NULL) AS closed
        FROM trades GROUP BY 1 ORDER BY 1
    """)
    data = [{
        'time': r['bucket'].isoformat(),
        'profit': float(r['profit']),
        'closed': r['closed']
    } for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/cumulative-profit')
def api_cumulative_profit():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        WITH hourly AS (
            SELECT date_trunc('hour', time) AS bucket,
                COALESCE(SUM(profit::numeric), 0) AS profit
            FROM trades WHERE profit IS NOT NULL
            GROUP BY 1 ORDER BY 1
        )
        SELECT bucket::text, profit,
            SUM(profit) OVER (ORDER BY bucket) AS cumulative
        FROM hourly ORDER BY bucket
    """)
    data = [{
        'time': r['bucket'],
        'profit': float(r['profit']),
        'cumulative': float(r['cumulative']),
    } for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/score-distribution')
def api_score_distribution():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT (score / 10 * 10) AS bucket, COUNT(*) AS count
        FROM trades WHERE score IS NOT NULL
        GROUP BY 1 ORDER BY 1
    """)
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/profit-by-hour')
def api_profit_by_hour():
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT EXTRACT(HOUR FROM time)::int AS hour,
            COALESCE(SUM(profit::numeric), 0) AS profit,
            COUNT(*) FILTER (WHERE profit IS NOT NULL) AS closed
        FROM trades GROUP BY 1 ORDER BY 1
    """)
    data = [{'hour': r['hour'], 'profit': float(r['profit']), 'closed': r['closed']} for r in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/recent-trades')
def api_recent_trades():
    symbol = request.args.get('symbol', '')
    limit = min(int(request.args.get('limit', 50)), 200)
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    if symbol:
        cur.execute("""
            SELECT time, symbol, type, lot, open_price, close_price, profit, score, comment
            FROM trades WHERE symbol = %s ORDER BY time DESC LIMIT %s
        """, (symbol, limit))
    else:
        cur.execute("""
            SELECT time, symbol, type, lot, open_price, close_price, profit, score, comment
            FROM trades ORDER BY time DESC LIMIT %s
        """, (limit,))
    data = []
    for r in cur.fetchall():
        data.append({
            'time': r['time'].isoformat() if r['time'] else None,
            'symbol': r['symbol'],
            'type': r['type'],
            'lot': float(r['lot']) if r['lot'] else None,
            'open_price': float(r['open_price']) if r['open_price'] else None,
            'close_price': float(r['close_price']) if r['close_price'] else None,
            'profit': float(r['profit']) if r['profit'] else None,
            'score': r['score'],
            'comment': r['comment'],
        })
    cur.close()
    conn.close()
    return jsonify(data)

@app.route('/api/csv')
def api_csv():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT time, symbol, type, lot, open_price, close_price, profit, score, comment
        FROM trades ORDER BY time DESC
    """)
    lines = ['time,symbol,type,lot,open_price,close_price,profit,score,comment']
    for r in cur.fetchall():
        p = f'{r[6]:.2f}' if r[6] is not None else ''
        lines.append(f'{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]},{p},{r[7]},{r[8]}')
    cur.close()
    conn.close()
    return '\n'.join(lines), 200, {'Content-Type': 'text/csv', 'Content-Disposition': 'attachment; filename=trades.csv'}

# ─── System API ────────────────────────────────────────────

PROM_QUERIES = {
    'cpu_usage': '100 - (avg(rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)',
    'memory_total': 'node_memory_MemTotal_bytes',
    'memory_available': 'node_memory_MemAvailable_bytes',
    'memory_free': 'node_memory_MemFree_bytes',
    'load1': 'node_load1',
    'load5': 'node_load5',
    'load15': 'node_load15',
    'boot_time': 'node_boot_time_seconds',
    'disk_total': 'node_filesystem_size_bytes{mountpoint="/"}',
    'disk_free': 'node_filesystem_free_bytes{mountpoint="/"}',
    'disk_total_data': 'node_filesystem_size_bytes{mountpoint="/data"}',
    'disk_free_data': 'node_filesystem_free_bytes{mountpoint="/data"}',
    'net_rx': 'rate(node_network_receive_bytes_total{device="eth0"}[5m])',
    'net_tx': 'rate(node_network_transmit_bytes_total{device="eth0"}[5m])',
    'processes': 'node_processes_running',
}

def get_prom_value(key):
    q = PROM_QUERIES.get(key)
    if not q: return None
    res = query_prometheus(q)
    if res.get('status') != 'success': return None
    results = res.get('data', {}).get('result', [])
    if not results: return None
    return float(results[0]['value'][1])

@app.route('/api/system')
def api_system():
    cpu = get_prom_value('cpu_usage')
    mem_total = get_prom_value('memory_total')
    mem_avail = get_prom_value('memory_available')
    mem_free = get_prom_value('memory_free')
    load1 = get_prom_value('load1')
    load5 = get_prom_value('load5')
    load15 = get_prom_value('load15')
    boot = get_prom_value('boot_time')
    disk_total = get_prom_value('disk_total')
    disk_free = get_prom_value('disk_free')
    disk_data_total = get_prom_value('disk_total_data')
    disk_data_free = get_prom_value('disk_free_data')
    net_rx = get_prom_value('net_rx')
    net_tx = get_prom_value('net_tx')
    procs = get_prom_value('processes')

    uptime_seconds = int(time.time() - boot) if boot else 0
    uptime_days = uptime_seconds // 86400
    uptime_hours = (uptime_seconds % 86400) // 3600

    mem_used = (mem_total - mem_avail) if mem_total and mem_avail else 0

    return jsonify({
        'cpu': round(cpu, 1) if cpu else None,
        'memory': {
            'total': round(mem_total / 1024**3, 1) if mem_total else None,
            'used': round(mem_used / 1024**3, 1) if mem_used else None,
            'available': round(mem_avail / 1024**3, 1) if mem_avail else None,
            'free': round(mem_free / 1024**3, 1) if mem_free else None,
            'percent': round(mem_used / mem_total * 100, 1) if mem_total and mem_used else None,
        },
        'load': {
            '1m': round(load1, 2) if load1 else None,
            '5m': round(load5, 2) if load5 else None,
            '15m': round(load15, 2) if load15 else None,
        },
        'uptime': {'seconds': uptime_seconds, 'days': uptime_days, 'hours': uptime_hours},
        'disk': {
            'total': round(disk_total / 1024**3, 1) if disk_total else None,
            'free': round(disk_free / 1024**3, 1) if disk_free else None,
            'used': round((disk_total - disk_free) / 1024**3, 1) if disk_total and disk_free else None,
            'percent': round((disk_total - disk_free) / disk_total * 100, 1) if disk_total and disk_free else None,
        },
        'disk_data': {
            'total': round(disk_data_total / 1024**3, 1) if disk_data_total else None,
            'free': round(disk_data_free / 1024**3, 1) if disk_data_free else None,
            'used': round((disk_data_total - disk_data_free) / 1024**3, 1) if disk_data_total and disk_data_free else None,
            'percent': round((disk_data_total - disk_data_free) / disk_data_total * 100, 1) if disk_data_total and disk_data_free else None,
        } if disk_data_total else None,
        'network': {
            'rx_bytes': round(net_rx, 0) if net_rx else None,
            'tx_bytes': round(net_tx, 0) if net_tx else None,
            'rx_kbps': round(net_rx / 1024, 1) if net_rx else None,
            'tx_kbps': round(net_tx / 1024, 1) if net_tx else None,
        } if net_rx else None,
        'processes': int(procs) if procs else None,
    })

@app.route('/api/system/history')
def api_system_history():
    duration = request.args.get('duration', '1h')
    queries = {
        'cpu': f'avg by (mode) (rate(node_cpu_seconds_total[5m])) * 100',
        'memory': 'node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes',
        'disk_io': 'rate(node_disk_io_time_seconds_total[5m])',
    }
    results = {}
    for key, q in queries.items():
        url = f'{PROM_URL}/api/v1/query?query={urllib.request.quote(q)}&time={urllib.request.quote(duration)}'
        try:
            with urllib.request.urlopen(url, timeout=5) as r:
                results[key] = json.loads(r.read())
        except:
            results[key] = {'status': 'error'}
    return jsonify(results)

def check_service(name, url, timeout=3):
    try:
        req = urllib.request.Request(url, method='HEAD')
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {'name': name, 'status': 'up', 'code': r.status, 'uptime': None}
    except Exception as e:
        return {'name': name, 'status': 'down', 'error': str(e), 'code': None}

def check_pg():
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT 1')
        cur.close()
        conn.close()
        return {'name': 'PostgreSQL', 'status': 'up'}
    except Exception as e:
        return {'name': 'PostgreSQL', 'status': 'down', 'error': str(e)}

@app.route('/api/services')
def api_services():
    services = [
        check_service('Dashboard', f'http://localhost:{os.environ.get("PORT", 9001)}/api/stats'),
        check_service('Grafana', 'http://grafana:3000/api/health'),
        check_service('Prometheus', 'http://prometheus:9090/-/ready'),
        check_service('Nginx', 'http://nginx-proxy:80/'),
        check_pg(),
    ]
    for s in services:
        if s.get('error'):
            s['error'] = str(s['error'])[:80]
    return jsonify(services)

# ─── Screenshots API ──────────────────────────────────────

def auth_ok():
    return request.args.get('key', '') == PASSWORD or request.headers.get('X-Key', '') == PASSWORD

@app.route('/api/uploads', methods=['GET'])
def api_uploads():
    files = []
    for f in sorted(os.listdir(UPLOAD_DIR), reverse=True):
        fp = os.path.join(UPLOAD_DIR, f)
        if os.path.isfile(fp):
            files.append({
                'name': f,
                'size': os.path.getsize(fp),
                'mtime': datetime.fromtimestamp(os.path.getmtime(fp)).isoformat(),
            })
    return jsonify(files)

@app.route('/api/uploads/new', methods=['GET'])
def api_uploads_new():
    state = {}
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            state = json.load(f)
    new = []
    for f in os.listdir(UPLOAD_DIR):
        if os.path.isfile(os.path.join(UPLOAD_DIR, f)) and f not in state:
            new.append(f)
    return jsonify(new)

@app.route('/api/uploads/<filename>', methods=['DELETE'])
def api_upload_delete(filename):
    if not auth_ok():
        return jsonify({'error': 'Unauthorized'}), 401
    fp = os.path.join(UPLOAD_DIR, filename)
    if os.path.isfile(fp):
        os.remove(fp)
        return jsonify({'ok': True})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/upload', methods=['POST'])
def api_upload():
    if not auth_ok():
        return jsonify({'error': 'Wrong password'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file'}), 400
    files = request.files.getlist('file')
    saved = []
    errors = []
    for f in files:
        if not f.filename:
            continue
        ext = os.path.splitext(f.filename)[1].lower()
        if ext not in ALLOWED_EXTS:
            errors.append(f'{f.filename}: invalid extension')
            continue
        content_length = f.content_length
        if content_length and content_length > MAX_SIZE:
            errors.append(f'{f.filename}: too large (>10MB)')
            continue
        try:
            dest = os.path.join(UPLOAD_DIR, f.filename)
            f.save(dest)
            if os.path.getsize(dest) > MAX_SIZE:
                os.remove(dest)
                errors.append(f'{f.filename}: too large (>10MB)')
                continue
            saved.append(f.filename)
        except Exception as e:
            errors.append(f'{f.filename}: {str(e)[:50]}')
    return jsonify({'saved': saved, 'errors': errors})

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(UPLOAD_DIR, filename)

# ─── Pages ─────────────────────────────────────────────────

@app.route('/')
def page_dashboard():
    return render_template('dashboard.html')

@app.route('/trading')
def page_trading():
    return render_template('trading.html')

@app.route('/system')
def page_system():
    return render_template('system.html')

@app.route('/settings')
def page_settings():
    return render_template('settings.html')

@app.route('/screenshots')
def page_screenshots():
    return render_template('screenshots.html', auth=auth_ok())

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9001))
    app.run(host='0.0.0.0', port=port, debug=False)
