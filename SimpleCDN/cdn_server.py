# cdn_server.py
import http.server
import socketserver
import requests
import os
import hashlib

PORT = 8000
ORIGIN_SERVER = "https://google.com"  # Change this to your origin server URL
CACHE_DIR = "cache"

class CachingProxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)

        # Generate a cache key from the request path
        # We use a hash to create a valid filename
        cache_key = hashlib.md5(self.path.encode('utf-8')).hexdigest()
        cache_file_path = os.path.join(CACHE_DIR, cache_key)
        
        # Check if the content is in our cache
        if os.path.exists(cache_file_path):
            print(f"Cache HIT for: {self.path}")
            with open(cache_file_path, 'rb') as f:
                content = f.read()
            
            # We need to also cache headers, for this simple example we'll guess the content type
            content_type = 'text/html' # A simple default
            if self.path.endswith(".css"):
                content_type = "text/css"
            elif self.path.endswith(".js"):
                content_type = "application/javascript"

            self.send_response(200)
            self.send_header('Content-type', content_type)
            self.end_headers()
            self.wfile.write(content)
            return

        # If not in cache, it's a Cache MISS
        print(f"Cache MISS for: {self.path}")
        try:
            # Forward the request to the origin server
            origin_url = ORIGIN_SERVER + self.path
            response = requests.get(origin_url, headers={'User-Agent': 'SimpleCDN/1.0'})

            if response.status_code == 200:
                # Save the response to our cache
                with open(cache_file_path, 'wb') as f:
                    f.write(response.content)

                # Serve the response to the client
                self.send_response(200)
                self.send_header('Content-type', response.headers.get('Content-Type', 'text/html'))
                self.end_headers()
                self.wfile.write(response.content)
            else:
                self.send_error(response.status_code)

        except requests.exceptions.RequestException as e:
            self.send_error(500, f"Error fetching from origin server: {e}")


with socketserver.TCPServer(("", PORT), CachingProxy) as httpd:
    print(f"Serving at port {PORT}")
    print(f"Origin server: {ORIGIN_SERVER}")
    httpd.serve_forever()
