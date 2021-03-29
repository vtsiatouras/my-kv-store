import click

from data_generator.data_generator import generated_key_value_pairs
from broker.broker import KeyValueBroker
from server.server import KeyValueServer
from tools.cli_tools import file_to_list, list_of_dicts_to_file
from tools.kv_tools import validate_ip_port


@click.group()
def cli():
    pass


@cli.command()
@click.option('-n', prompt=True, required=True, type=click.INT,
              help='Indicates the number of lines (i.e. separate data) that we would like to generate')
@click.option('-d', prompt=True, required=True, type=click.INT,
              help='Is the maximum level of nesting (i.e. how many times in a line a value can have  a set of '
                   'key : values). Zero means no nesting, i.e. there is only one set of key-values per line '
                   '(in the value of the high level key).')
@click.option('-m', prompt=True, required=True, type=click.INT, help='Is the maximum number of keys inside each value.')
@click.option('-l', prompt=True, required=True, type=click.INT,
              help='Is the maximum length of a string value whenever you need to generate a string. For example 4 '
                   'means that we can generate Strings of up to length 4 (e.g. "ab", "abcd", "a"). We should '
                   'not generate empty strings (i.e. "" is not correct). Strings can be only letters (upper and '
                   'lowercase) and numbers. No symbols.')
@click.option('-k', prompt=True, type=click.File(),
              help='A file containing a space-separated list of key names and their data types that we can '
                   'potentially use for creating data.')
def create_data(n, d, m, l, k):
    click.echo('Creating data')
    click.echo(f'n: {n}, d: {d}, m: {m}, l: {l}, k: {k}')
    fields_list = file_to_list(k)
    print(fields_list)
    generated_key_values = generated_key_value_pairs(number_of_lines=n, level_of_nesting=d, max_number_of_keys=m,
                                                     max_word_length=l, key_names=fields_list)
    list_of_dicts_to_file(generated_key_values)


@click.option('-a', prompt=True, required=True, type=click.STRING, help='The IP address')
@click.option('-p', prompt=True, required=True, type=click.INT, help='The port')
@cli.command()
def kv_server(a, p):
    validate_ip_port(ip_address=a, port=p)
    server = KeyValueServer(ip_address=a, port=p)
    server.serve()


# @click.option('-s', prompt=True, required=True, type=click.File(), help='File that indicates the servers to connect')
# @click.option('-i', prompt=True, required=True, type=click.File(), help='File that contains data to store')
# @click.option('-k', prompt=True, required=True, type=click.INT, help='Replication factor, how many different'
#                                                                      'servers will have the same replicated data')
@cli.command()
def kv_broker():
    servers = [('127.0.0.1', 5000), ('127.0.0.1', 5001)]
    broker = KeyValueBroker(servers=servers, replication_factor=1)
    broker.send_request_to_servers()


if __name__ == '__main__':
    cli()
