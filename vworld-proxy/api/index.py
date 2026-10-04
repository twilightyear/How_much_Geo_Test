from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests

class handler(BaseHTTPRequestHandler):
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')

    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()

    def do_GET(self):
        print(f"[Vercel Proxy Log] Raw self.path: {self.path}")
        
        parsed_path = urlparse(self.path)
        clean_path = parsed_path.path.rstrip('/')
        
        # Vworld 타겟 URL 구성
        target_url = f"https://api.vworld.kr{clean_path}"
        if parsed_path.query:
            target_url += f"?{parsed_path.query}"
            
        print(f"[Vercel Proxy Log] Target Vworld URL: {target_url}")
        
        try:
            # Vworld 접근 거부 방지를 위한 헤더
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': 'https://vworld.kr'
            }

            response = requests.get(
                target_url,
                headers=headers,
                timeout=10,
                allow_redirects=True
            )
            
            print(f"[Vercel Proxy Log] Vworld Status: {response.status_code}")

            self.send_response(response.status_code)
            self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json; charset=utf-8'))
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"[Vercel Proxy Error] {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self._set_cors_headers()
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
