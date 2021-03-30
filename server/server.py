from socketserver import StreamRequestHandler, TCPServer
from time import sleep

from tools.general_tools import validate_ip_port


class RequestHandler(StreamRequestHandler):

    def handle(self):
        while True:
            if not self.rfile.peek():
                break
            sleep(5)
            data = self.rfile.readline().strip()
            print("{} wrote: {}".format(self.client_address[0], data))
            # Likewise, self.wfile is a file-like object used to write back
            # to the client
            self.wfile.write(data.upper())


class KeyValueServer:

    def __init__(self, ip_address, port):
        validate_ip_port(ip_address, port)
        self.ip_address = ip_address
        self.port = port
        self.server = TCPServer(server_address=(self.ip_address, self.port), RequestHandlerClass=RequestHandler)

    def serve(self):
        self.server.serve_forever()
