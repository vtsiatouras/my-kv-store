from typing import List, Any, Union


class TrieNode:

    def __init__(self):
        self.children = dict()
        self.is_terminal = False
        self.value = None  # Instantiates only when the node is terminal


class Trie:

    def __init__(self):
        self.root = TrieNode()

    def insert(self, key: str, value: Any) -> None:
        """ Trie insert operation.
        :param key: The key to insert
        :param value: The value to store
        :return: None
        """
        tokens = [ch for ch in key]
        node = self.root
        for token in tokens:
            if token not in node.children:
                node.children[token] = TrieNode()
            node = node.children[token]

        node.is_terminal = True
        node.value = value

    def delete(self, key: str) -> bool:
        """ Trie delete operation.
        :param key: The key to delete
        :return: Boolean
        """
        tokens = [ch for ch in key]
        node = self.root
        for token in tokens:
            # Not found
            if not node:
                return False
            node = node.children.get(token)

        if not node:
            # Not found
            return False
        else:
            node.is_terminal = False
            node.value = None   # Let the Garbage Collector handle this mess :)
            return True

    def search(self, key: str) -> Any:
        """ Trie search operation.
        :param key: The key to search
        :return: The value or None if not found
        """
        tokens = [ch for ch in key]
        node = self.root
        for token in tokens:
            # Not found
            if not node:
                return None
            node = node.children.get(token)

        return node.value if node and node.is_terminal else None

    def dfs(self, node: TrieNode, prefix: str, items_dict: dict) -> None:
        """ Depth First Search recursive method that returns a dict of all the keys, values given a starting node
        :param node: A node to start
        :param prefix: The prefix that is built upon the recursion
        :param items_dict: The list that contains key value pairs passed as param to built through the recursion
        :return: The final list that contains all the key value pairs of the trie
        """
        if node.is_terminal:
            val = node.value
            if type(node.value) is Trie:
                items_ = dict()
                self.dfs(node.value.root, '', items_)
                val = items_
            items_dict.update({prefix: val})
        for child in node.children:
            self.dfs(node.children.get(child), prefix + child, items_dict)

    def search_by_keys(self, keys: List) -> Union[dict, str]:
        """ Given a list of keys search iteratively from the 1st tier trie to all the nested tries.
        If the list contains 1 item returns all the nested key/value pairs. Returns None if no results were found.
        :param keys: List of keys to search sequentially
        :return: The value
        """
        trie_index = self
        value = ''
        for key in keys:
            value = trie_index.search(key)
            if type(value) is Trie:
                trie_index = value

        if type(value) is Trie:
            items_ = dict()
            self.dfs(value.root, '', items_)
            value = items_

        return value

    def insert_dict(self, dictionary: dict) -> None:
        """ Given a dictionary inserts to the main Trie and creates nested sub-Tries if needed to save the nested
        key/value pairs
        :param dictionary: The dictionary to save
        :return: None
        """
        trie_index = self
        for key, value in dictionary.items():
            # If the dict contains nested dicts create sub Trie
            if type(value) is dict:
                trie_ = Trie()
                trie_.insert_dict(value)
                value = trie_
            trie_index.insert(key, value)


############################################################################
if __name__ == '__main__':
    trie = Trie()
    trie.insert_dict({'test': {'nested_key': 'val1'}})
    trie.insert_dict({'test2': {'nested_key': 'val2'}})
    trie.insert_dict({'text': {'nested_key': 'another val'}})
    trie.insert_dict({'asdf': {'nested_key': {'subnested_key': 'value', 'subnested_key2': 'value2',
                                              'subnested_key3': 'value2'}, 'subnested_key': 'value'}})

    items = {}
    trie.dfs(trie.root, '', items)
    print(items)

    print(trie.search_by_keys(['asdf']))
    print(trie.search_by_keys(['asdf', 'nested_key']))
    print(trie.search_by_keys(['asdf', 'nested_key', 'subnested_key2']))
    print(trie.search_by_keys(['asdf', 'nested_key', 'subnested_key2sasasa']))
    print(trie.search_by_keys(['asdadasdf']))
    print(trie.search_by_keys(['asdf', 'dasdadas']))

    if trie.delete('text'):
        print('deleted')
    if not trie.delete('asdasdfa'):
        print('not deleted')

    print(trie.search('test'))
    print(trie.search('test2'))
    print(trie.search('text'))
    print(trie.search('asdf'))
    print(trie.search('NOt exist'))
    print(trie.search('123134124'))
