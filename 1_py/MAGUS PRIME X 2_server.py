import http.server
import socketserver

PORT = 8085


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # If root path or index.html is requested, serve the startup_animation.html
        if self.path == "/" or self.path == "/index.html":
            self.path = "/startup_animation.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


Handler = MyHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    print("Open your browser to see the MAGUS PRIME X animated intro")
    httpd.serve_forever()
