from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote, urlencode
import requests

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.end_headers()

    def do_GET(self):
        # 1. unquote 처리
        decoded_raw_path = unquote(self.path)
        print(f"[Vercel Proxy] Original raw path: {decoded_raw_path}")

        parsed_path = urlparse(decoded_raw_path)
        query_dict = parse_qs(parsed_path.query)

        # 2. Vercel이 path=? 형태로 넘겨준 경로 추출 및 제거
        endpoint_path = parsed_path.path.rstrip('/')
        
        # 만약 path 파라미터가 쿼리에 들어가 있다면 실제 경로로 추출
        if 'path' in query_dict:
            extracted_path = query_dict.pop('path')[0]  # 'req/data' 또는 'ned/data/...'
            endpoint_path = f"/{extracted_path.lstrip('/')}"
        
        # 만약 endpoint_path가 /api/index.py 형태로 남아있다면 제거
        if endpoint_path.startswith('/api/index'):
            endpoint_path = ''

        # 3. 깨끗해진 쿼리 스트링 다시 조립
        # parse_qs로 분해된 리스트 값들을 다시 단일 값 형태의 쿼리 스트링으로 변환
        clean_query_params = {k: v[0] for k, v in query_dict.items() if v}
        clean_query_string = urlencode(clean_query_params)

        # 4. 최종 Vworld Target URL 생성
        target_url = f"https://api.vworld.kr{endpoint_path}"
        if clean_query_string:
            target_url += f"?{clean_query_string}"

        print(f"[Vercel Proxy] Final Target URL: {target_url}")

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(
                target_url,
                headers=headers,
                timeout=10,
                allow_redirects=True
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
