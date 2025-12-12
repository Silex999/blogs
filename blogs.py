import re
from http.server import SimpleHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
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
            (r'^/static/(.*)$', self.serve_file),
        ]

        for pattern, view in routes:
            if re.match(pattern, path):
                return view(path, parse)

        return super().do_GET()

    def do_POST(self):
        parse = urlparse(self.path)
        path = parse.path

        if path == '/add-blog':
            return self.add_blog()
        else:
            self.send_error(404)

    def add_blog(self):
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            params = parse_qs(post_data.decode('utf-8'))
            
            title = params.get('title', [''])[0]
            date = params.get('date', [''])[0]
            summary = params.get('summary', [''])[0]
            content = params.get('content', [''])[0]
            
            blogs_file = 'blogs/blogs.json'
            os.makedirs('blogs', exist_ok=True)
            
            if os.path.exists(blogs_file):
                with open(blogs_file, 'r', encoding='utf-8') as f:
                    blogs = json.load(f)
            else:
                blogs = []
            
            if blogs:
                max_id = max([blog.get('id', 0) for blog in blogs if isinstance(blog.get('id'), int)], default=0)
                new_id = max_id + 1
            else:
                new_id = 1
            
            new_blog = {
                "id": new_id,
                "title": title,
                "date": date if date else datetime.now().strftime('%Y-%m-%d'),
                "summary": summary,
                "content": content
            }
            
            blogs.append(new_blog)
            
            with open(blogs_file, 'w', encoding='utf-8') as f:
                json.dump(blogs, f, ensure_ascii=False, indent=2)
            
            self.send_response(303)
            self.send_header('Location', '/')
            self.end_headers()
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            error_html = f'<p>Ошибка: {str(e)}</p><a href="/">Назад</a>'
            self.wfile.write(error_html.encode('utf-8'))

    def index(self, path=None, parse=None):
        try:
            blogs_file = 'blogs/blogs.json'
            if os.path.exists(blogs_file):
                with open(blogs_file, 'r', encoding='utf-8') as f:
                    blogs = json.load(f)
            else:
                blogs = []
            
            blog_list_html = ''
            for blog in blogs:
                blog_list_html += f'''
                <li>
                    <a href="/{blog['id']}">{blog['title']} — {blog['date']}</a>
                    <p>{blog['summary']}</p>
                </li>
                '''
            
            with open('templates/index.html', 'r', encoding='utf-8') as f:
                template = f.read()
            
            html = template.replace('{{BLOG_LIST}}', blog_list_html)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Ошибка: {str(e)}")

    def blog(self, path, parse):
        try:
            blog_id = int(path.lstrip('/'))
            
            blogs_file = 'blogs/blogs.json'
            if os.path.exists(blogs_file):
                with open(blogs_file, 'r', encoding='utf-8') as f:
                    blogs = json.load(f)
            else:
                blogs = []
            
            blog = next((b for b in blogs if b.get('id') == blog_id), None)
            
            if not blog:
                self.send_response(404)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write('<p>Пост не найден</p><a href="/">Назад</a>'.encode('utf-8'))
                return
            
            with open('templates/blog.html', 'r', encoding='utf-8') as f:
                template = f.read()
            
            html = template.replace('{{TITLE}}', blog['title'])
            html = html.replace('{{DATE}}', blog['date'])
            html = html.replace('{{CONTENT}}', blog['content'])
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(html.encode('utf-8'))
            
        except Exception as e:
            self.send_error(500, f"Ошибка: {str(e)}")

    def serve_file(self, path, parse):
        self.path = '/' + path.lstrip('/')
        return super().do_GET()

def run(server_class=HTTPServer, handler_class=SimpleHTTPRequestHandler):
    httpd = server_class(('', 8000), handler_class)
    httpd.serve_forever()

if __name__ == "__main__":
    print('start server')
    run(HTTPServer, MyHandler)