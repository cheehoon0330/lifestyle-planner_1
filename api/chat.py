import json
import os
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            prompt = body.get('prompt', '')

            api_key = os.environ.get('ANTHROPIC_API_KEY', '')
            if not api_key:
                self._respond(500, {'error': 'API key not configured'})
                return

            payload = json.dumps({
                'model': 'claude-sonnet-4-5',
                'max_tokens': 2800,
                'messages': [{'role': 'user', 'content': prompt}]
            }).encode('utf-8')

            req = urllib.request.Request(
                'https://api.anthropic.com/v1/messages',
                data=payload,
                headers={
                    'Content-Type': 'application/json',
                    'x-api-key': api_key,
                    'anthropic-version': '2023-06-01'
                },
                method='POST'
            )

            with urllib.request.urlopen(req) as res:
                data = json.loads(res.read().decode('utf-8'))
                text = data['content'][0]['text']
                self._respond(200, {'result': text})

        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode('utf-8'))
            self._respond(e.code, {'error': err.get('error', {}).get('message', str(e))})
        except Exception as e:
            self._respond(500, {'error': str(e)})

    def _respond(self, code, data):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))
