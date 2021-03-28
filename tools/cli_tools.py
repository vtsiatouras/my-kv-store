from typing import List


def validate_keyfile_types(keyfile_type):

    if keyfile_type not in ['string', 'float', 'int']:
        raise Exception(f'Unknown type {keyfile_type} found at your key-file. '
                        f'Allowed types are: "string", "float", "int"')


def file_to_list(file):

    lst = list()
    for line in file:
        words = line.split()
        key_ = words[0]
        type_ = words[1]
        try:
            validate_keyfile_types(type_)
        except Exception:
            exit(1)
        lst.append((key_, type_))

    return lst


def list_of_dicts_to_file(list_of_dicts: List[dict]):
    with open("dataset.txt", "w") as outfile:
        for dictionary in list_of_dicts:
            # Cast dict to str & remove curly braces from the start and the end
            line = str(dictionary)[1:-1].replace(',', ';')
            outfile.write(f'{line}\n')
