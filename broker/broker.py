import socket
import multiprocessing as mp

from typing import List
from random import sample
from tools.general_tools import validate_ip_port


class KeyValueBroker:

    def __init__(self, servers, replication_factor):
        for ip, port in servers:
            validate_ip_port(ip_address=ip, port=port)

        self.servers = servers
        self.replication_factor = replication_factor

    def send_request_to_servers(self, data):
        # Choose k random servers
        random_servers = sample(self.servers, k=self.replication_factor)
        # Send requests in parallel
        processes = 4
        with mp.Pool(processes=processes) as p:
            params = [(ip, port, data) for ip, port in random_servers]
            results = p.map(self.send, params)
            print(results)

    def index_procedure(self, data: List[tuple]):
        for line in data:
            payload = f'PUT {line}'
            self.send_request_to_servers(payload)

    @staticmethod
    def send(args):
        ip, port, data = args
        print(ip, port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                # Connect to server and send data
                sock.connect((ip, port))
                sock.sendall(bytes(data + "\n", "utf-8"))

                # Receive data from the server and shut down
                received = b''
                while True:
                    part = sock.recv(1024)
                    received += part
                    if len(part) < 1024:
                        # either 0 or end of data
                        received = str(received, "utf-8")
                        break

            except ConnectionRefusedError:
                print(f'Server with IP: {ip} at port: {port} refused to connect')
                return 'CONNECTION REFUSED'

            finally:
                print("Sent:     {}".format(data))
                print("Received: {}".format(received))
