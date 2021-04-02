import sys
from socketserver import StreamRequestHandler, TCPServer
from typing import Tuple, Any

from server.trie import Trie
from tools.general_tools import (
    validate_ip_port,
    parse_command_for_server,
    CustomValidationException,
)


class RequestHandler(StreamRequestHandler):
    def handle(self):
        while True:
            if not self.rfile.peek():
                break
            payload = self.rfile.readline().strip()
            result = self.server.process_command(
                self.client_address, str(payload, "utf-8")
            )
            self.wfile.write(bytes(result, "utf-8"))


class KeyValueServer(TCPServer):
    def __init__(self, server_address: Tuple[str, int]):
        validate_ip_port(*server_address)
        super().__init__(
            server_address=server_address, RequestHandlerClass=RequestHandler
        )
        self.trie_index = Trie()

    def serve(self):
        self.serve_forever()

    def process_command(self, client_address: Any, payload: str) -> str:
        try:
            command, data = parse_command_for_server(payload)
            print(f"{client_address} invoked {command} {data}")
            if command in ["GET", "QUERY"]:
                # Maybe it is redundant but just check in any case...
                if command == "GET" and len(data) > 1:
                    raise CustomValidationException("Malformed data")
                result = self.trie_index.search_by_keys(data)
                return str(result) if result else "NOT FOUND"
            elif command == "PUT":
                self.trie_index.insert_dict(data)
                return "OK"
            elif command == "DELETE":
                # Maybe it is redundant but just check in any case...
                if len(data) > 1:
                    raise CustomValidationException("Malformed data")
                result = self.trie_index.delete(data[0])
                return "OK" if result else "NOT FOUND"
            else:
                return "ERROR"
        except CustomValidationException as e:
            print(e, file=sys.stderr)
            return "ERROR"
