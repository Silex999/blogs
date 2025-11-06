import re
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import os

class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        parse = urlparse(self.path)
        path = parse.path

        routes = [
            (r'^/$', self.index),
            (r'^/(\d+)$', self.blog),
            (r'^/blogs/(.*)$', self.serve_file),
            (r'^/static/(.*)$', self.serve_file),
        ]

        for pattern, view in routes:
            if re.match(pattern, path):
                return view(path, parse)

        return super().do_GET()

    def index(self, path=None, parse=None):
        self.path = '/templates/index.html'
        return super().do_GET()

    def blog(self, path, parse):
        blog_id = path.lstrip('/')

        target = '/templates/blog.html'
        if os.path.exists(self.translate_path(target)):
            self.path = target
            return super().do_GET()
        else:
            self.response(404)

    def response(self, code: int):
        self.send_response(code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def serve_file(self, path, parse):
        self.path = '/' + path.lstrip('/')
        return super().do_GET()

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    httpd = server_class(('', 8000), handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    print('start server')
    run(HTTPServer, MyHandler)