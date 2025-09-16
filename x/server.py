# light_server.py
import http.server
import socketserver
import urllib.request
import urllib.parse
import os

PORT = 5173
DIST_DIR = "dist"  # build 后的目录
API_BACKEND = "https://termux-be.codeusbxx.xyz"  # 后端 API 地址

class ProxyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy_request()
        else:
            # SPA fallback
            if self.path != "/" and not os.path.exists(os.path.join(DIST_DIR, self.path.lstrip("/"))):
                self.path = "/index.html"
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_request()
        else:
            self.send_error(405, "Method Not Allowed")

    def proxy_request(self):
        # 构造后端 URL
        url = f"{API_BACKEND}{self.path}"
        content_length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(content_length) if content_length > 0 else None

        req = urllib.request.Request(url, data=data, method=self.command)
        # 转发 headers
        for key, val in self.headers.items():
            if key.lower() != 'host':
                req.add_header(key, val)

        try:
            with urllib.request.urlopen(req) as res:
                self.send_response(res.status)
                # 转发后端 headers
                for header in res.getheaders():
                    if header[0].lower() not in ["content-length", "transfer-encoding", "connection"]:
                        self.send_header(header[0], header[1])
                # 添加 CORS 头
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(res.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())

    # 支持 OPTIONS 方法（CORS preflight）
    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

# 启动服务器
os.chdir(DIST_DIR)
with socketserver.TCPServer(("", PORT), ProxyHTTPRequestHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    httpd.serve_forever()
