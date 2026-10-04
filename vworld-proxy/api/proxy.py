from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import requests

ALLOWED_PATHS = {
    "/req/data",
    "/req/wfs",
    "/req/wms",
    "/ned/data/getLandCharacteristics",
    "/ned/data/getIndvdLandPrice",
}

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path not in ALLOWED_PATHS:
            self.send_error(404, "Unsupported V-World endpoint")
            return

        query = parse_qs(parsed.query)
        params = {key: values[0] for key, values in query.items() if values}

        # API 키를 포함할 수 있는 query 값은 로그로 남기지 않습니다.
        print(f"[Vercel Proxy] path={path}, param_names={list(params.keys())}")

        target_url = f"https://api.vworld.kr{path}"

        try:
            response = requests.get(
                target_url,
                params=params,
                timeout=10,
                allow_redirects=True,
            )

            print(
                f"[Vercel Proxy] status={response.status_code}, "
                f"redirects={[r.status_code for r in response.history]}, "
                f"content_type={response.headers.get('Content-Type')}"
            )

            self.send_response(response.status_code)
            self.send_header(
                "Content-Type",
                response.headers.get("Content-Type", "application/octet-stream"),
            )
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(response.content)

        except requests.RequestException as exc:
            print(f"[Vercel Proxy] upstream request failed: {type(exc).__name__}")
            self.send_error(502, "V-World upstream request failed")
