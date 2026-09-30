from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Vercel로 들어온 요청의 쿼리 파라미터 파싱
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        
        # 쿼리 파라미터 리스트 형태를 단일 값으로 변환 (requests용)
        params = {k: v[0] for k, v in query_params.items()}
        
        target_url = "https://api.vworld.kr/req/data"
        
        try:
            # 브이월드 API 호출 (타임아웃 10초)
            response = requests.get(target_url, params=params, timeout=10)
            
            # 응답 전달
            self.send_response(response.status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*') # CORS 허용
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(str({"error": str(e)}).encode('utf-8'))
        return
