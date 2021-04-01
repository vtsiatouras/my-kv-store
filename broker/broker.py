import socket
import click
import time
import multiprocessing as mp
import threading as td

from typing import List, Union
from random import sample
from tools.general_tools import validate_ip_port


class KeyValueBroker:

    def __init__(self, servers, replication_factor):
        for ip, port in servers:
            validate_ip_port(ip_address=ip, port=port)

        self.servers = servers
        self.replication_factor = replication_factor
        self.online_servers = []

        t = td.Thread(name='daemon-server-watchdog', target=self.__server_watchdog)
        t.setDaemon(True)
        t.start()

        # Make sure that we have at least k servers online before continuing
        while len(self.online_servers) < self.replication_factor:
            continue

    def __server_watchdog(self) -> None:
        """ Daemon function that checks the given servers are online. Performs a connect operation to each of them
        periodically and stores the online servers to the self.online_servers list.
        :return: None
        """
        while True:
            for server in self.servers:
                ip, port = server
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    try:
                        # Connect to server and send data
                        sock.connect((ip, port))
                        if server not in self.online_servers:
                            self.online_servers.append(server)
                    except ConnectionRefusedError:
                        if server in self.online_servers:
                            self.online_servers.remove(server)

            time.sleep(5)

    @staticmethod
    def __send__(args):
        """ Sends a command to a server and collects the response
        :param args: Tuple, unpack to ip, port, payload
        :return: The response of the server
        """
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

                return received

            except ConnectionRefusedError:
                print(f'Server with IP: {ip} at port: {port} refused to connect')
                return 'CONNECTION REFUSED'

    # TODO return results
    def __send_request_to_servers(self, payload: str, all_servers: bool = True, processes: int = 4):
        """ Sends a given request to the servers. The send procedure executes in parallel to the servers in order to
        avoid an iterative approach. This is necessary because we don't maintain the connection to servers throughout
        the whole runtime of the broker, but we invoke new connections when a new request is inserted.
        :param payload: The payload in str in format <CMD> <str(DATA: dict/list)>
        :param all_servers: Flag that indicates if the operation will be applied to all servers or to some of them
        (replication factor)
        :param processes: The number of parallel processes to execute simultaneously to many servers
        :return:
        """
        print(self.online_servers)
        servers_ = self.online_servers
        # Choose k random servers
        if not all_servers and len(self.online_servers) >= self.replication_factor:
            servers_ = sample(servers_, k=self.replication_factor)
        # Send requests in parallel
        with mp.Pool(processes=processes) as p:
            params = [(ip, port, payload) for ip, port in servers_]
            results = p.map(self.__send__, params)
            print(results)

    def print_servers_warning(self) -> None:
        """ Prints an alert message when the available online servers are less than the replication factor threshold.
        THE METHOD IS CALLED AT THE CLI AFTER THE USER INPUT IN ORDER TO AVOID UGLY PRINTS!!
        :return: None
        """
        if len(self.online_servers) < self.replication_factor:
            msg = click.style('WARNING: online servers: {}!'.format(len(self.online_servers)), fg='red')
            print(f'{msg : >50}')

    def execute_command(self, command: str, data: Union[dict, list]) -> None:
        """ Executes a parsed command from the CLI
        :param command: The validated command
        :param data: The validated data in dictionary type
        :return: None
        """
        if command == 'PUT':
            self.__send_request_to_servers(f'{command} {data}', all_servers=False)
        else:
            self.__send_request_to_servers(f'{command} {data}', all_servers=True)

    def index_procedure(self, data: List[tuple]) -> None:
        """ Performs indexing operation when a data file is given
        :param data: The validated list of tuples that contains the data
        :return: None
        """
        for line in data:
            payload = f'PUT {line}'
            self.__send_request_to_servers(payload, all_servers=False)
