# My KeyValue Store

[![python](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue.svg)](https://img.shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9-blue.svg)   [![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This project is a custom implementation of a Key Value Store (Redis like) and is not intended for any production usage. 
Below you can find enlisted installation instructions, how to use this app & some key parts of the implementation of this project
that are worth to mention.


## Installation

This section contains the installation instructions in order to set up a local environment. The instructions
have been validated for Ubuntu 20.04.

First, install all required software with the following command:

```bash
sudo apt update
sudo apt install git python3 python3-pip python3-dev
```

The project dependencies are managed with [pipenv](https://docs.pipenv.org/en/latest/). You can install it with:

```bash
pip install --user pipenv
```

`pipenv` should now be in your `PATH`. If not, logout and log in again. Then install all dependencies with:

```bash
pipenv install --dev
```

Then you can enable the python environment with:

```bash
pipenv shell
```

**All commands from this point forward require the python environment to be enabled.**


## Usage

The project contains 3 different submodules that can be manipulated through the supported CLI. 

- Data creation module: creates randomized datasets of key/value pairs
- Key Value Server: accepts and executes given queries
- Key Value Broker: manages the available connections to Key Value servers

So, lets teardown briefly each part!

### Data Creation module

This module generates randomized key value pairs in order to use them as initial input data to test the KeyValue DB. 
The following is an example of how the generated data looks like.

```
'person_0': {'status': 'c2Qz9'; 'profession': '1r'; 'street': 'WBIi'; 'weight': 766.3485392245253; 'country': 'R'}
'person_1': {'age': 710; 'profession': 'f'; 'height': 237.5070598177147; 'gender': 'BthiN'; 'address': {'name': {'profession': '701'; 'company': 's'}}}
'person_2': {'nationality': 'mRQv'; 'department': 'YBsj6'; 'weight': {'weight': {'level': {'profession': 'SCOWk'; 'address': {'age': {'salary': 625.5442450963857}; 'phone_number': 258; 'street': 'HoQuK'; 'weight': 481.6002715796077}}}; 'age': 107; 'department': {'weight': 453.5015133666217; 'name': 'YF1Z'; 'street': '3h8'; 'rating': {'address': 'KNbF'; 'status': 'iIv'; 'age': 916; 'rating': 435}}; 'gender': {'gender': {'grade': {'position': 'NF7'; 'status': 'mR'}; 'gender': 'HG5Je'}; 'weight': 309.5693783158633; 'name': {'age': 91; 'level': 653}; 'degree': {'profession': 'X8q'; 'level': 719}; 'grade': {'department': 'ErA'; 'level': {'street': '3'; 'status': 'l'; 'address': 'Hw7'; 'country': 'FVDJQ'}; 'salary': {'degree': 'YyS'}; 'name': 'ccSp'}}}; 'address': 'bC1'}
'person_3': {'nationality': 'rF4V'}
'person_4': {'height': 739.8379923345368}
```

As you have noticed these key/value pairs are non-sense (remember we want only to stress test the database with mock
data). In order to actually generate data by yourself, initially you should prepare a file that contain the basic 
keys to use and their type. 

Here you can see an example of this key-file:

```
name string
age int
height float
weight float
street string
```

The data generator validates if any of these keys have an unknown data type. The accepted types are `string`, `int` & `float`. 
Although you may have noticed that in the mock data above many keys have as value a nested key/value pair. 
This is required by the given specification to add a small probability to create nested k/v pairs in a maximum depth 
and with maximum number of pairs.

**Example:**

```bash
python cli.py create-data -n 1000 -d 5 -m 5 -l 5 -k keyFile.txt
```

- `-n`: Indicates the number of lines (i.e. separate data) that we would like to generate
- `-d`: Is the maximum level of nesting (i.e. how many times in a line a value can have a set of key: values). 
  Zero means no nesting, i.e. there is only one set of key-values per line (in the value of the high level key).
- `-m`: Is the maximum number of keys inside each value.
- `-l`: Is the maximum length of a string value whenever you need to generate a string. For example 4 means that we can generate Strings 
  of up to length 4 (e.g. "ab", "abcd", "a"). We should not generate empty strings (i.e. "" is not correct). Strings can be only letters 
  (upper and lowercase) and numbers. No symbols.
- `-k`: A file containing a space-separated list of key names, and their data types that we can potentially use for creating data.

### Key Value Server module

This module contains the "heart" of this project. This is a typical TCP server that accepts requests from a broker through socket level. In order to store
the data and retrieve them efficiently the server uses an internal in memory data-structure that is based on [Tries](https://en.wikipedia.org/wiki/Trie).

The below paradigm presents how k/v pairs are stored internally.

```
'text': {'ant': {'sub': 1}; 'and': 'value2'}
'test': {'any': 'value3'}
```

<p align="center">
  <img src="https://github.com/VangelisTsiatouras/my-kv-store/blob/main/assist_material/tries.png">
</p>

As you have noticed in the diagram above, the nested k/v pairs are stored to nested Trie indices too, increasing the efficiency of the search operation.

**Example:**

```bash
python cli.py kv-server -a 127.0.0.1 -p 5000
```

- `-a`: The IP address
- `-p`: The port

### Key Value Broker module

This module is the main interface between the user and the servers. In order to avoid data loss and have a continuous backup plan in case of 
failure of a server, broker replicates the data we want to store in a number of servers that the user defines. The servers are checked repeatedly
about their state, and the user will be informed if many servers are unreachable. The way this is implemented is by having a daemon service that 
checks in every 2 seconds all the servers. Also, the broker in order to push a command to the N number of servers, will execute the "_establish connection, 
send request, receive results & close connection_" procedure in parallel. This design choice allows us to send a given request to many servers very quickly,
without maintaining continuous connections with the servers throughout the runtime of the broker.

**Example:**

```bash
python cli.py kv-broker -s servers.txt -k 2 -i dataset.txt
```

- `-s`: File that indicates the servers to connect
- `-k`: Replication factor, how many different servers will have the same replicated data
- `-i`: File that contains data to store [Optional]

The `servers.txt` is a file that contains IP, port pairs, it is validated that the IP/ports are correct, and the broker will not start if any of the
servers defined is not reachable (I decided to make it a bit strict). Also, the broker after the initialization procedure will provide to the user a 
command prompt which can be used to execute various operations. These operations are:

```
PUT 'key': {'key1': 'value'}
GET key
QUERY key.key1
DELETE key
```

Some things about the accepted syntax. 

`PUT`, `GET`, `QUERY` & `DELETE` can be written to lowercase too.

The accepted pattern of defining a k/v pair at `PUT` command is:`'<top_level_key>': {'<key1>':<value1> ; '<key2>':<value2>}`, where top `top_level_key` 
is required to be written alone without curly brackets, use `;` to separate the k/v pairs and in `value` the user can put either an actual string/int/float 
value, or a nested k/v pair. Also, all keys should be enclosed with quotes `'`.

The accepted pattern of `GET` and `DELETE` is just write down any key you want to delete without quotes or anything

Finally, the accepted pattern of `QUERY` is to write a number of keys separated with dot `.` without quotes.

Concluding, I must refer that on `PUT` operation the broker pushes the given k/v pair to k randomly picked servers 
and also that `DELETE` operation requires all the servers to be available.  

### Execution Screenshots

Below there are some screenshots on how the CLI looks like.

_Normal execution_

![screen1](https://github.com/VangelisTsiatouras/my-kv-store/blob/main/assist_material/screen_1.png)

_Error when starting with server down_

![screen2](https://github.com/VangelisTsiatouras/my-kv-store/blob/main/assist_material/screen_3.png)

_Some syntax errors_

![screen3](https://github.com/VangelisTsiatouras/my-kv-store/blob/main/assist_material/screen_4.png)

_Warning when we have a few replicated servers_

![screen4](https://github.com/VangelisTsiatouras/my-kv-store/blob/main/assist_material/screen_2.png)

_Warning at delete operation when having at least 1 server down_ 

![screen5](https://github.com/VangelisTsiatouras/my-kv-store/blob/main/assist_material/screen_5.png)
