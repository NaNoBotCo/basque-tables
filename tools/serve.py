"""Serve build/ for a look. python3 tools/serve.py [port]"""
import functools, http.server, os, socketserver, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8802))
root = C.DOCS if os.environ.get("SERVE_DOCS") else C.BUILD
class H(http.server.SimpleHTTPRequestHandler):
    """Serve the build under the same base path the published site uses, so a link
    that works here works there. That is the bug this guards: a GitHub project page
    lives under /<repo>/, and a root-relative link on it lands on the user site."""

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=root, **kw)

    def translate_path(self, path):
        if C.BASE and (path == C.BASE or path.startswith(C.BASE + "/")):
            path = path[len(C.BASE):] or "/"
        return super().translate_path(path)

    def do_GET(self):
        if C.BASE and self.path == "/":
            self.send_response(302)
            self.send_header("Location", C.BASE + "/")
            self.end_headers()
            return
        super().do_GET()
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", port), H) as httpd:
    print("serving %s on http://localhost:%d%s/" % (root, port, C.BASE))
    httpd.serve_forever()
