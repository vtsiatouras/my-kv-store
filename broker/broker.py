import socket
import time
import multiprocessing as mp
import threading as td

from typing import List, Union, Optional
from random import sample
from tools.general_tools import (
    validate_ip_port,
    print_warning_messages,
    merge_server_results,
    CustomBrokerConnectionException,
)


class KeyValueBroker:
    def __init__(self, servers: List[tuple], replication_factor: int):
        for ip, port in servers:
            validate_ip_port(ip_address=ip, port=port)

        self.servers = servers
        self.replication_factor = replication_factor
        self.online_servers = []

        # Check that the given servers are reachable
        self.__servers_check(raise_connection_error=True)

        # Processes Pool that will be used to assign parallel requests to servers
        self.pool = mp.Pool(processes=4)

        # Initiating thread for checking the health of the servers
        self.pause_daemon = False
        self.pause_cond = td.Condition(td.Lock())
        self.daemon = td.Thread(
            name="daemon-server-watchdog", target=self.__server_watchdog, daemon=True
        )
        self.daemon.start()

        # Make sure that we have at least k servers online before continuing.
        while len(self.online_servers) < self.replication_factor:
            continue

    def __server_watchdog(self) -> None:
        """Daemon function that checks the given servers are online.
        :return: None
        """
        while True:
            # Pause Condition Variable
            with self.pause_cond:
                while self.pause_daemon:
                    self.pause_cond.wait()
            # Server checking
            self.__servers_check(raise_connection_error=False)
            time.sleep(2)

    def __pause_watchdog(self) -> None:
        self.pause_daemon = True
        self.pause_cond.acquire()

    def __resume_watchdog(self) -> None:
        self.pause_daemon = False
        self.pause_cond.notify()
        self.pause_cond.release()

    def __servers_check(self, raise_connection_error: bool = False) -> None:
        """Performs a connect operation to each of them periodically and stores the online servers to the
        self.online_servers list.
        :return: None
        """
        for server in self.servers:
            ip, port = server
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                try:
                    # Connect to server and send data
                    sock.connect((ip, port))
                    if server not in self.online_servers:
                        self.online_servers.append(server)
                except (ConnectionRefusedError, ConnectionResetError) as e:
                    if raise_connection_error:
                        raise CustomBrokerConnectionException(f'Server {ip}:{port} not reachable.\n{e}')
                    if server in self.online_servers:
                        self.online_servers.remove(server)

    @staticmethod
    def __send__(args):
        """Sends a command to a server and collects the response
        :param args: Tuple, unpack to ip, port, payload
        :return: The response of the server
        """
        ip, port, payload = args
        print(ip, port)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                # Connect to server and send data
                sock.connect((ip, port))
                sock.sendall(bytes(payload + "\n", "utf-8"))

                # Receive data from the server and shut down
                received = b""
                while True:
                    part = sock.recv(1024)
                    received += part
                    if len(part) < 1024:
                        # either 0 or end of data
                        received = str(received, "utf-8")
                        break

                return received

            except (ConnectionRefusedError, ConnectionResetError) as e:
                print(f"Server {ip}:{port} not reachable\n{e}")
                return "CONNECTION REFUSED"

    def __send_request_to_servers(
        self, payload: str, all_servers: bool = True
    ) -> List[str]:
        """Sends a given request to the servers. The send procedure executes in parallel to the servers in order to
        avoid an iterative approach. This is necessary because we don't maintain the connection to servers throughout
        the whole runtime of the broker, but we invoke new connections when a new request is inserted.
        :param payload: The payload in str in format <CMD> <str(DATA: dict/list)>
        :param all_servers: Flag that indicates if the operation will be applied to all servers or to some of them
        (replication factor)
        :return: A list of the received results
        """
        servers_ = self.online_servers
        # Choose k random servers
        if not all_servers and len(self.online_servers) >= self.replication_factor:
            servers_ = sample(servers_, k=self.replication_factor)
        # Send requests in parallel
        params = [(ip, port, payload) for ip, port in servers_]
        results = self.pool.map(self.__send__, params)
        return results

    def print_servers_warning(self) -> None:
        """Prints an alert message when the available online servers are less than the replication factor threshold.
        THE METHOD IS CALLED AT THE CLI AFTER THE USER INPUT IN ORDER TO AVOID UGLY PRINTS!!
        :return: None
        """
        if len(self.online_servers) < self.replication_factor:
            print_warning_messages(
                "WARNING: online servers: {}/{}".format(
                    len(self.online_servers), len(self.servers)
                )
            )

    def execute_command(self, command: str, data: Union[dict, list]) -> Optional[str]:
        """Executes a parsed command from the CLI
        :param command: The validated command
        :param data: The validated data in dictionary type
        :return: The result
        """
        # Stop daemon server watchdog
        self.__pause_watchdog()

        if command == "PUT":
            results = self.__send_request_to_servers(
                f"{command} {data}", all_servers=False
            )
        else:
            # Prevent delete operation when we have even one server down!
            if command == "DELETE" and (self.online_servers != self.servers):
                print_warning_messages(
                    "WARNING: online servers: {}/{} ABORTING DELETE OPERATION".format(
                        len(self.online_servers), len(self.servers)
                    )
                )
                # Resume daemon
                self.__resume_watchdog()
                return None

            results = self.__send_request_to_servers(
                f"{command} {data}", all_servers=True
            )

        # Resume daemon
        self.__resume_watchdog()

        return merge_server_results(results)

    def index_procedure(self, data: List[tuple]) -> None:
        """Performs indexing operation when a data file is given
        :param data: The validated list of tuples that contains the data
        :return: None
        """
        # Stop daemon server watchdog
        self.__pause_watchdog()

        # Send data to servers
        for line in data:
            payload = f"PUT {line}"
            self.__send_request_to_servers(payload, all_servers=False)

        # Resume daemon
        self.__resume_watchdog()
