from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests

class handler(BaseHTTPRequestHandler):
    # CORS 공통 헤더 설정 Helper
    def _set_cors_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')

    # 1. CORS Preflight (OPTIONS) 요청 처리
    def do_OPTIONS(self):
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
        return

    # 2. GET 요청 처리
    def do_GET(self):
        print(f"[Vercel Proxy] Received raw path: {self.path}")
        
        parsed_path = urlparse(self.path)
        
        # 경로 끝의 트레일링 슬래시(/) 제거 (예: /req/data/ -> /req/data)
        clean_path = parsed_path.path.rstrip('/')
        
        # 원본 쿼리 스트링을 그대로 유지하여 Vworld Target URL 생성
        target_url = f"https://api.vworld.kr{clean_path}"
        if parsed_path.query:
            target_url += f"?{parsed_path.query}"
            
        print(f"[Vercel Proxy] Forwarding to Target URL: {target_url}")
        
        try:
            # 브라우저 요청 헤더 전달 (User-Agent, Referer)
            headers = {
                'User-Agent': self.headers.get('User-Agent', 'Mozilla/5.0'),
            }
            if self.headers.get('Referer'):
                headers['Referer'] = self.headers.get('Referer')

            # Vworld API 호출
            response = requests.get(
                target_url,
                headers=headers,
                timeout=10,
                allow_redirects=True,
            )
            
            print(f"[Vercel Proxy] Vworld Response Status: {response.status_code}")
            
            # 클라이언트에 응답 전달
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
        return
