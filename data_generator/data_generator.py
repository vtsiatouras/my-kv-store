import string

from random import randrange, choice, choices, randint, uniform, random
from typing import List, Union


def get_values(value_type: str, max_word_length: int) -> Union[str, int, float]:
    """Returns a random value to be assigned for a key
    :param value_type: The type of the value
    :param max_word_length: If the type is 'string' this defines the max length of the created word
    :return: The value
    """
    if value_type == "int":
        return randint(0, 1000)
    elif value_type == "float":
        return uniform(0.0, 1000.0)
    elif value_type == "string":
        word_length = randint(1, max_word_length)
        return "".join(choices(string.ascii_uppercase + string.digits, k=word_length))


def create_dictionary(
    level_of_nesting: int,
    max_number_of_keys: int,
    max_word_length: int,
    key_names: List[tuple],
    current_level,
) -> dict:
    """This method creates inner key-value pairs (dictionaries) and also it supports nesting key-value creation using
    recursion.
    :param level_of_nesting: The maximum level of nesting
    :param max_number_of_keys: The maximum number of keys for a level
    :param max_word_length: The maximum word length for 'string' values
    :param key_names: A list that contains the key names
    :param current_level: The current level of nesting. This is used as Recursion Rule.
    :return: The dictionary that contains key-value pairs
    """

    num_of_keys = randrange(1, max_number_of_keys + 1)
    dictionary = dict()
    for _ in range(num_of_keys):

        # Avoid appending duplicate keys on the same level
        while True:
            key_w_type = choice(key_names)
            if key_w_type[0] not in dictionary:
                break

        # Insert value or a nested dict. Nested dict should be created if we have available level nesting and
        # the random number is below 0.35 in order to avoid too many nested dicts
        if current_level < level_of_nesting and random() < 0.35:
            dictionary[key_w_type[0]] = create_dictionary(
                level_of_nesting,
                max_number_of_keys,
                max_word_length,
                key_names,
                current_level + 1,
            )
        else:
            dictionary[key_w_type[0]] = get_values(key_w_type[1], max_word_length)

    return dictionary


def generated_key_value_pairs(
    number_of_lines: int,
    level_of_nesting: int,
    max_number_of_keys: int,
    max_word_length: int,
    key_names: List[tuple],
) -> List[dict]:
    """Top level method that creates the 1st level key value pairs. Also it invokes the method create_dictionary
    in order to save the inner key-value pairs and returns the whole created dataset.
    :param number_of_lines: The number of lines to create
    :param level_of_nesting: The maximum level of nesting
    :param max_number_of_keys: The maximum number of keys for a level
    :param max_word_length: The maximum word length for 'string' values
    :param key_names: A list that contains the key names
    :return: The dictionary that contains the whole created dataset
    """

    records = list()
    for it in range(number_of_lines):
        records.append(
            {
                f"person_{it}": create_dictionary(
                    level_of_nesting, max_number_of_keys, max_word_length, key_names, 0
                )
            }
        )

    return records
