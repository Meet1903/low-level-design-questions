class Node:
    def __init__(self, key = None, value = None):
        self.key = key
        self.value = value
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = {}

        self.head = Node()
        self.tail = Node()

        self.head.next = self.tail
        self.tail.prev = self.head
    
    def _remove_node(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev
    
    def _add_to_head(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node
    
    def get(self, key):
        if key not in self.cache:
            return -1
        node = self.cache[key]
        self._remove_node(node)
        self._add_to_head(node)

        return node.value
    
    def put(self, key, value):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove_node(node)
            self._add_to_head(node)
            return
        
        if len(self.cache) == self.capacity:
            lru_node = self.tail.prev
            self._remove_node(lru_node)
            del self.cache[lru_node.key]
        
        new_node = Node(key, value)
        self.cache[key] = new_node
        self._add_to_head(new_node)

if __name__ == '__main__':
    print("LRU Cache Demonstration:")
    cache = LRUCache(2)

    cache.put(1, 1)
    cache.put(2, 2)

    print(f"Get 1: {cache.get(1)}")  # returns 1
    
    cache.put(3, 3)  # LRU key was 2, evicts key 2, cache is {1=1, 3=3}
    print(f"Get 2: {cache.get(2)}")  # returns -1 (not found)
    
    cache.put(4, 4)  # LRU key was 1, evicts key 1, cache is {4=4, 3=3}
    print(f"Get 1: {cache.get(1)}")  # returns -1 (not found)
    print(f"Get 3: {cache.get(3)}")  # returns 3
    print(f"Get 4: {cache.get(4)}") 
