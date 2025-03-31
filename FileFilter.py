from typing import List

class File:
    def __init__(self, name: str, size: int, file_type: int, is_directory: bool, children: List['File'] = None):
        self.name = name
        self.size = size
        self.file_type = file_type
        self.is_directory = is_directory
        self.children = children if children is not None else []

    def __repr__(self):
        return f"File(name={self.name}, size={self.size}, type={self.file_type}, is_directory={self.is_directory})"

class Filter:
    def apply(self, file: File) -> bool:
        raise NotImplementedError("Subclasses must implement this method")

class MinSizeFilter(Filter):
    def __init__(self, min_size: int):
        self.min_size = min_size

    def apply(self, file: File) -> bool:
        return file.size > self.min_size

class TypeFilter(Filter):
    def __init__(self, file_type: int):
        self.file_type = file_type

    def apply(self, file: File) -> bool:
        return file.file_type == self.file_type

class NotADirectoryException(Exception):
    pass

class FindCommand:
    def find_with_filters(self, directory: File, filters: List[Filter], include_directories: bool = False) -> List[File]:
        """
        Recursively search for files in a given directory that satisfy all filters.
        
        Parameters:
          directory: The root File to search within (must be a directory).
          filters: A list of Filter objects to apply.
          include_directories: If True, directories are also checked against filters.
        
        Returns:
          A list of File objects that satisfy all filter conditions.
        """
        if not directory.is_directory:
            raise NotADirectoryException("The provided file is not a directory")

        output: List[File] = []
        self._find_with_filters(directory, filters, output, include_directories)
        return output

    def _find_with_filters(self, directory: File, filters: List[Filter], output: List[File], include_directories: bool):
        for file in directory.children:
            # If the file is a directory, optionally apply filters, then search recursively.
            if file.is_directory:
                if include_directories and all(f.apply(file) for f in filters):
                    output.append(file)
                self._find_with_filters(file, filters, output, include_directories)
            else:
                if all(f.apply(file) for f in filters):
                    output.append(file)

# Example usage:
if __name__ == "__main__":
    # Create sample file hierarchy:
    file1 = File("file1.txt", 120, 1, False)
    file2 = File("file2.log", 80, 2, False)
    file3 = File("file3.txt", 200, 1, False)
    subdir = File("subdir", 0, 0, True, children=[file2])
    root = File("root", 0, 0, True, children=[file1, file3, subdir])

    # Define filters: Find files with size greater than 100 and of type 1.
    filters: List[Filter] = [MinSizeFilter(100), TypeFilter(1)]

    find_cmd = FindCommand()
    found_files = find_cmd.find_with_filters(root, filters)
    print("Found files:", found_files)