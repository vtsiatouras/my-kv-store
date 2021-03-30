import ast

from typing import List, Tuple
from socket import inet_aton, error as socket_error


class CustomValidationException(Exception):
    pass


def validate_keyfile_types(keyfile_type):

    if keyfile_type not in ['string', 'float', 'int']:
        raise CustomValidationException(f'Unknown type {keyfile_type} found at your key-file. '
                                        f'Allowed types are: "string", "float", "int"')


def validate_ip_port(ip_address: str, port: str) -> None:
    try:
        port_ = int(port)
    except ValueError:
        raise ValueError
    if not 0 < port_ < 65535:
        raise CustomValidationException('-p must be an integer, ranging from 0 to 65535')
    try:
        inet_aton(ip_address)
    except socket_error:
        raise socket_error


def parse_command(command: str) -> Tuple:
    command_parts = command.split(' ', 1)
    if command_parts[0] not in ['GET', 'QUERY', 'DELETE', 'PUT']:
        raise CustomValidationException('Available commands are: "GET", "QUERY", "DELETE", "PUT"')
    return command_parts[0], string_to_dict(command_parts[1])


def serialize_data_from_file(file) -> List:
    data = list()
    for line in file:
        data.append(string_to_dict(line))
    return data


def file_to_list(file):
    lst = list()
    for line in file:
        words = line.split()
        key_ = words[0]
        type_ = words[1]
        try:
            validate_keyfile_types(type_)
        except CustomValidationException:
            exit(1)
        lst.append((key_, type_))
    return lst


def string_to_dict(string: str) -> dict:
    str_dict = '{' + string + '}'
    str_dict = str_dict.replace(';', ',')
    dictionary = ast.literal_eval(str_dict)
    if type(dictionary) is not dict:
        raise CustomValidationException('Data should be complaint to the following pattern\n'
                                        '\'<key>\': {\'key_1\': \'value_1\'; \'key_1\': \'value_2\';}')
    return dictionary


def list_of_dicts_to_file(list_of_dicts: List[dict]):
    with open("dataset.txt", "w") as outfile:
        for dictionary in list_of_dicts:
            # Cast dict to str & remove curly braces from the start and the end
            line = str(dictionary)[1:-1].replace(',', ';')
            outfile.write(f'{line}\n')


def read_servers_from_file(file) -> List[tuple]:
    servers = list()
    for line in file:
        server_parts = line.split()
        try:
            validate_ip_port(ip_address=server_parts[0], port=server_parts[1])
        except (CustomValidationException, ValueError, socket_error) as e:
            print(e)
            continue
        servers.append((server_parts[0], int(server_parts[1])))

    return servers
