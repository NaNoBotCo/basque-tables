"""Serve build/ for a look. python3 tools/serve.py [port]"""
import functools, http.server, os, socketserver, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C

port = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8802))
root = C.DOCS if os.environ.get("SERVE_DOCS") else C.BUILD
H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=root)
socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", port), H) as httpd:
    print("serving %s on http://localhost:%d/" % (root, port))
    httpd.serve_forever()
