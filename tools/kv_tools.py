from socket import inet_aton, error as socket_error


def validate_ip_port(ip_address, port):
    if not 0 < port < 65535:
        raise Exception('-p must be an integer, ranging from 0 to 65535')
    try:
        inet_aton(ip_address)
    except socket_error:
        raise socket_error
