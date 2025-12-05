import re
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import os
import json
from datetime import datetime

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

    def add_blog(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            blogs_file = 'blogs/blogs.json'
            
            os.makedirs('blogs', exist_ok=True)
            
            if os.path.exists(blogs_file):
                with open(blogs_file, 'r', encoding='utf-8') as f:
                    blogs = json.load(f)
            else:
                blogs = []
            
            if blogs:
                max_id = 0
                for blog in blogs:
                    try:
                        blog_id = blog.get('id', 0)
                        if isinstance(blog_id, int) and blog_id > max_id:
                            max_id = blog_id
                    except (ValueError, TypeError):
                        continue
                new_id = max_id + 1
            else:
                new_id = 1
            
            new_blog = {
                "id": new_id,
                "title": data.get('title', ''),
                "date": data.get('date', datetime.now().strftime('%Y-%m-%d')),
                "summary": data.get('summary', ''),
                "content": data.get('content', '')
            }
            
            blogs.append(new_blog)
            
            with open(blogs_file, 'w', encoding='utf-8') as f:
                json.dump(blogs, f, ensure_ascii=False, indent=2)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            response = json.dumps({"success": True, "message": "Блог успешно добавлен", "id": new_id})
            self.wfile.write(response.encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.end_headers()
            response = json.dumps({"success": False, "error": str(e)})
            self.wfile.write(response.encode('utf-8'))

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