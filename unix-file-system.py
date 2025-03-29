import time

class Node:
    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.creation_time = time.time()  # Placeholder for creation time
        self.modification_time = time.time()  # Placeholder for modification time
        self.permissions = {
            'read': True,
            'write': True,
            'execute': False
        }
    
    def set_permissions(self, read: bool, write: bool, execute: bool):
        self.permissions['read'] = read
        self.permissions['write'] = write
        self.permissions['execute'] = execute
    
    def update_modification_time(self):
        self.modification_time = time.time()
    
class Directory(Node):
    def __init__(self, name, parent=None):
        super().__init__(name)
        self.parent = parent
        self.children = {}
    
    def add_child(self, child):
        if not isinstance(child, Node):
            raise TypeError("Child must be an instance of Node")
        self.children[child.name] = child
        child.parent = self

class File(Node):
    def __init__(self, name, parent=None):
        super().__init__(name)
        self.parent = parent
        self.content = ""
        self.size = 0  
    
    def add_content(self, content: str):
        self.content += content
        self.size = len(self.content)

    def read_content(self):
        return self.content

class FileSystem:
    def __init__(self):
        self.root = Directory('')
    
    def _traverse(self, path: str) -> Node:
        if path == '/':
            return self.root

        parts = [part for part in path.split("/") if part]

        node = self.root

        for part in parts:
            if part in node.children:
                node = node.children[part]
            else:
                raise FileNotFoundError("Path does not exists")
        return node

    def ls(self, path):
        node = self._traverse(path)
        return sorted(node.children.keys())

    def mkdir(self, path):
        parts = [part for part in path.split("/") if part]
        node = self.root
        for part in parts:
            if part not in node.children:
                new_dir = Directory(part)
                new_dir.parent = node
                node.children[part] = new_dir
                node.update_modification_time()
            node = node.children[part]
    
    def addContentToFile(self, filePath, content):
        parts = [part for part in filePath.split("/") if part]
        node = self.root
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                if part not in node.children:
                    new_file = File(part)
                    new_file.parent = node
                    node.children[part] = new_file
                    node.update_modification_time()
            else:
                if part not in node.children:
                    new_dir = Directory(part)
                    new_dir.parent = node
                    node.children[part] = new_dir
                    node.update_modification_time()
                node = node.children[part]
    
    def readContentFromFile(self, filePath):
        node = self._traverse(filePath)
        return node.content
    
    def get_metadata(self, path):
        node = self._traverse(path)
        return {
            'name': node.name,
            'creation_time': node.creation_time,
            'modification_time': node.modification_time,
            'size': node.size if node.size else 0,
            'permission': node.permissions,
            'type': 'File' if node.size else 'Directory'
        }
    
if __name__ == '__main__':
    fs = FileSystem()
    fs.mkdir('/a/b/c')
    fs.addContentToFile("/a/b/c/d.txt", "Hello, World!")
    print("Contents of '/a/b/c':", fs.ls("/a/b/c"))
    print("Metadata of '/a/b/c/d.txt':", fs.get_metadata("/a/b/c/d.txt"))
    print("Content of '/a/b/c/d.txt':", fs.readContentFromFile("/a/b/c/d.txt"))
