import base64
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = 8000

CONFIG_FILE = "all_configs.txt"


def load_configs():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        lines = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]
    return lines


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/sub":
            configs = load_configs()

            # объединяем в текст
            raw = "\n".join(configs)

            # кодируем в base64 (ВАЖНО!)
            encoded = base64.b64encode(raw.encode()).decode()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(encoded.encode())
        else:
            self.send_response(404)
            self.end_headers()


def run():
    server = HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"Server started: http://localhost:{PORT}/sub")
    server.serve_forever()


if __name__ == "__main__":
    run()