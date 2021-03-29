import socket
import multiprocessing as mp

from tools.kv_tools import validate_ip_port


class KeyValueBroker:

    def __init__(self, servers, replication_factor):
        for ip, port in servers:
            validate_ip_port(ip_address=ip, port=port)

        self.servers = servers
        self.replication_factor = replication_factor

    def send_request_to_servers(self):
        processes = 4
        with mp.Pool(processes=processes) as p:
            data = f'this is a test'
            params = [(ip, port, data) for ip, port in self.servers]
            results = p.map(self.send, params)

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
                received = str(sock.recv(1024), "utf-8")
            except ConnectionRefusedError:
                print(f'Server with IP: {ip} at port: {port} refused to connect')
                pass

        print("Sent:     {}".format(data))
        print("Received: {}".format(received))
