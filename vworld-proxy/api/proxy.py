from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print(f"[Vercel Proxy] Received raw path: {self.path}")
        
        parsed_path = urlparse(self.path)
        
        # 1. 경로 끝의 중복 슬래시(/) 제거
        clean_path = parsed_path.path.rstrip('/')
        
        # 2. Vworld Target URL 생성
        target_url = f"https://api.vworld.kr{clean_path}"
        if parsed_path.query:
            target_url += f"?{parsed_path.query}"
            
        print(f"[Vercel Proxy] Target URL: {target_url}")
        
        try:
            headers = {
                'User-Agent': self.headers.get('User-Agent', 'Mozilla/5.0'),
            }
            if self.headers.get('Referer'):
                headers['Referer'] = self.headers.get('Referer')

            response = requests.get(
                target_url,
                headers=headers,
                timeout=10,
                allow_redirects=True,
            )
            
            print(f"[Vercel Proxy] Vworld Response Status: {response.status_code}")
            
            self.send_response(response.status_code)
            self.send_header('Content-Type', response.headers.get('Content-Type', 'application/json; charset=utf-8'))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"[Vercel Proxy Error] {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(f'{{"error": "{str(e)}"}}'.encode('utf-8'))
        return
