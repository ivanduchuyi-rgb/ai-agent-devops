from http.server import BaseHTTPRequestHandler
import json, urllib.parse

def make_handler(get_fn=None, post_fn=None, delete_fn=None):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, fmt, *args):
            pass
        def _request(self, method):
            parsed = urllib.parse.urlparse(self.path)
            params = dict(urllib.parse.parse_qsl(parsed.query))
            body = None
            if method in ('POST', 'PUT', 'PATCH'):
                n = int(self.headers.get('Content-Length', 0) or 0)
                if n:
                    body = self.rfile.read(n).decode()
            return {
                'method': method,
                'path': parsed.path,
                'headers': {k.lower(): v for k, v in self.headers.items()},
                'queryStringParameters': params,
                'body': body,
            }
        def _respond(self, resp):
            body = resp.get('body', '')
            hdrs = resp.get('headers', {})
            self.send_response(resp.get('statusCode', 200))
            for k, v in hdrs.items():
                self.send_header(k, v)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Key')
            self.end_headers()
            self.wfile.write(body.encode() if isinstance(body, str) else body)
        def do_OPTIONS(self):
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, X-Key')
            self.end_headers()
        def do_GET(self):
            self._respond(get_fn(self._request('GET'))) if get_fn else (self.send_response(405), self.end_headers())
        def do_POST(self):
            self._respond(post_fn(self._request('POST'))) if post_fn else (self.send_response(405), self.end_headers())
        def do_DELETE(self):
            self._respond(delete_fn(self._request('DELETE'))) if delete_fn else (self.send_response(405), self.end_headers())
    return Handler
