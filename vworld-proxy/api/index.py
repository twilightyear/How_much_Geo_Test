from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests
from urllib.parse import urlparse, parse_qs, unquote

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        # Vercel이 전달해준 원본 경로 그대로 사용
        parsed_path = urlparse(self.path)
        clean_path = parsed_path.path.rstrip('/')

        target_url = f"https://api.vworld.kr{clean_path}"
        
        if parsed_path.query:
            target_url += f"?{parsed_path.query}"
            
        print(f"[Vercel Proxy] Target URL: {target_url}")
        
        try:
            # Vworld 거부 방지용 헤더
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(
                target_url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )
            
            self.send_response(response.status_code)
            self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json; charset=utf-8'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
