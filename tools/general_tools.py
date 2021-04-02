import ast

from typing import List, Tuple, Dict
from socket import inet_aton, error as socket_error


class CustomValidationException(Exception):
    pass


def validate_keyfile_types(keyfile_type: str) -> None:
    """Validates if a given type from a key file is string", "float" or "int"
    :param keyfile_type: The type to check
    :return: None
    """
    if keyfile_type not in ["string", "float", "int"]:
        raise CustomValidationException(
            f"Unknown type {keyfile_type} found at your key-file. "
            f'Allowed types are: "string", "float", "int"'
        )


def validate_ip_port(ip_address: str, port: str) -> None:
    """Validates a set of IP address and a port
    :param ip_address: The IP address
    :param port: The port
    :return: None
    """
    try:
        port_ = int(port)
    except ValueError as e:
        raise CustomValidationException(e)
    if not 0 < port_ < 65535:
        raise CustomValidationException(
            "-p must be an integer, ranging from 0 to 65535"
        )
    try:
        inet_aton(ip_address)
    except socket_error as e:
        raise e


def parse_command(command: str) -> Tuple:
    """Parses a given command and checks for errors. Returns a tuple: (<CMD>, <DATA>)
    :param command: The given command
    :return: A tuple that at 0 index is placed the command in str ('GET', 'PUT', etc.) & at 1 index is placed
    serialized input data
    """
    command_parts = command.split(" ", 1)
    if command_parts[0] not in ["GET", "QUERY", "DELETE", "PUT"]:
        raise CustomValidationException(
            'Available commands are: "GET", "QUERY", "DELETE", "PUT"'
        )

    if command_parts[0] == "PUT":
        return command_parts[0], data_string_to_dict(command_parts[1])
    else:
        data_list = data_string_to_list(command_parts[1])
        if command_parts[0] in ["GET", "DELETE"] and len(data_list) > 1:
            raise CustomValidationException(
                f"{command_parts[0]} accepts only one key as parameter"
            )
        return command_parts[0], data_list


def parse_command_for_server(command: str) -> Tuple:
    """Parses a socket level command and checks for errors. Returns a tuple: (<CMD>, <DATA>)
    :param command: The given command
    :return: A tuple that at 0 index is placed the command in str ('GET', 'PUT', etc.) & at 1 index is placed
    serialized input data
    """
    command_parts = command.split(" ", 1)
    if command_parts[0] not in ["GET", "QUERY", "DELETE", "PUT"]:
        raise CustomValidationException(
            'Available commands are: "GET", "QUERY", "DELETE", "PUT"'
        )
    try:
        data = ast.literal_eval(command_parts[1])
        if (command_parts[0] == "PUT" and type(data) is dict) or (
            command_parts[0] in ["GET", "DELETE", "QUERY"] and type(data) is list
        ):
            return command_parts[0], data
        else:
            raise CustomValidationException("Malformed data received")
    except (ValueError, SyntaxError, TypeError) as e:
        raise CustomValidationException(e)


def read_data_from_file(file) -> List:
    """Reads data from a data file and performs validation. Each line is transformed to a dictionary.
    :param file: The file to serialize
    :return: A list of dictionaries
    """
    data = list()
    for line in file:
        try:
            data.append(data_string_to_dict(line))
        except CustomValidationException as e:
            print(f"{e}\nRecord ignored...")
            continue

    return data


def read_keys_and_types_from_file(file) -> List[tuple]:
    """Reads a key file and extracts the keys along with their types to a list of tuples
    :param file: The key file
    :return: A list of tuples
    """
    lst = list()
    for line in file:
        words = line.split()
        key_ = words[0]
        type_ = words[1]
        try:
            validate_keyfile_types(type_)
        except CustomValidationException as e:
            raise e
        lst.append((key_, type_))

    return lst


def read_servers_from_file(file) -> List[tuple]:
    """Reads server settings from a file and validates them for proper values
    :param file: The file that contains the servers
    :return: A list of tuples that contains the legit servers that found on the file
    """
    servers = list()
    for line in file:
        server_parts = line.split()
        try:
            validate_ip_port(ip_address=server_parts[0], port=server_parts[1])
        except (CustomValidationException, ValueError, socket_error) as e:
            print(f"{e}\nServer ignored...")
            continue
        servers.append((server_parts[0], int(server_parts[1])))

    return servers


def data_string_to_list(string_data: str) -> List:
    """Transforms a data string of the form key1.key2.key3 to list. Validation checks are applied here.
    :param string_data: The data string
    :return: The serialized data as a single list
    """
    return string_data.split(".")


def data_string_to_dict(
    string_data: str,
) -> Dict:
    """Transforms a data string of the form 'person1': {'height': 1.75; 'profession': 'student'} to dictionary.
    Validation checks are applied here.
    :param string_data: The data string
    :return: The serialized data as a single dictionary
    """
    str_dict = "{" + string_data + "}"
    str_dict = str_dict.replace(";", ",")
    try:
        dictionary = ast.literal_eval(str_dict)
    except (ValueError, SyntaxError, TypeError) as e:
        raise CustomValidationException(e)
    if type(dictionary) is not dict:
        raise CustomValidationException(
            "Data should be complaint to the following pattern\n"
            "'<key>': {'key_1': 'value_1'; 'key_1': 'value_2';}"
        )

    # Check if the inserted dict is not one level: 'key': 'value'
    for k, v in dictionary.items():
        if type(v) is not dict:
            raise CustomValidationException(
                "Data should be complaint to the following pattern\n"
                "'<key>': {'key_1': 'value_1'; 'key_1': 'value_2';}\n"
                "No single level key/values are allowed (e.g. 'key_1': 'value_1')"
            )

    return dictionary


def list_of_dicts_to_file(list_of_dicts: List[dict]) -> None:
    """Prints a list of dictionaries to the form 'person1': {'height': 1.75; 'profession': 'student'} to a data file.
    This is used to data generator package
    :param list_of_dicts: The list of dictionaries to write to file
    :return: None
    """
    with open("dataset.txt", "w") as outfile:
        for dictionary in list_of_dicts:
            # Cast dict to str & remove curly braces from the start and the end
            line = str(dictionary)[1:-1].replace(",", ";")
            outfile.write(f"{line}\n")
