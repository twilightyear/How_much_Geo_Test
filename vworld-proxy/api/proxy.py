from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # 1. 들어온 전체 path와 query 로그 출력
        print(f"[Vercel Proxy] Received raw path: {self.path}")
        
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)
        print(f"[Vercel Proxy] Parsed query_params dict: {query_params}")
        
        # 2. 안전하게 단일 값 추출 (값이 리스트 형태일 때 첫 번째 값 가져오기)
        params = {}
        for k, v in query_params.items():
            if v and len(v) > 0:
                params[k] = v[0]
                
        print(f"[Vercel Proxy] Cleaned params for Vworld: {params}")
        
        # 만약 key가 아예 빠져있다면 방어 코드 (환경변수나 하드코딩된 백업 키를 쓸 수도 있음)
        if "key" not in params:
            print("[Vercel Proxy Warning] 'key' parameter is missing from the request!")

        target_url = f"https://api.vworld.kr{parsed_path.path}"
        
        try:
            # 브이월드 API 호출 (타임아웃 10초)
            response = requests.get(
                target_url,
                params=params,
                timeout=10,
                allow_redirects=True,
            )
            print(f"[Vercel Proxy] Vworld Response Status: {response.status_code}")
            
            # 응답 전달
            self.send_response(response.status_code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*') # CORS 허용
            self.end_headers()
            self.wfile.write(response.content)
            
        except Exception as e:
            print(f"[Vercel Proxy Error] {str(e)}")
            self.send_response(500)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(str({"error": str(e)}).encode('utf-8'))
        return
