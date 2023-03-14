import http.server
import socketserver
import json

PORT = 8080

class MyRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/get-ip":
            response_data = {"ip": self.client_address[0]}
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())
        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), MyRequestHandler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
