import http.server
import threading

class RedirectHandler(http.server.SimpleHTTPRequestHandler):
    """Handles redirect response to capture authCode and userId."""
    auth_code = None
    user_id = None
    login_received = threading.Event()
    current_server = None
    
    def do_GET(self):
        from urllib.parse import urlparse, parse_qs
        query = parse_qs(urlparse(self.path).query)
        RedirectHandler.auth_code = query.get("authCode", [None])[0]
        RedirectHandler.user_id = query.get("userId", [None])[0]
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<h2>Login successful. You may close this tab.</h2>")
        RedirectHandler.login_received.set()
