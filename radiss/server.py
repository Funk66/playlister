from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import BaseServer
from threading import Thread

from . import log


class HTTPRequestHandler(BaseHTTPRequestHandler):
    server: BaseServer
    spotify_code: str

    def do_GET(self):
        HTTPRequestHandler.spotify_code = self.path.split('=')[1]
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", 'text/html')
        self.end_headers()
        Thread(target=shutdown, args=(self.server, )).start()


def listen() -> str:
    bind = ("", 8888)
    with HTTPServer(bind, HTTPRequestHandler) as HTTPRequestHandler.server:
        log.info("Listening for authentication callback")
        HTTPRequestHandler.server.serve_forever()
    return HTTPRequestHandler.spotify_code


def shutdown(server):
    server.shutdown()
