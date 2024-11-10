from contextlib import contextmanager
import os
from typing import TextIO, Generator


class FileContext:
    """
    Provides a safe context for file operations.

    This class offers a context manager for safely opening, handling, and closing files.
    It ensures proper file management even in case of exceptions and logs file operations.

    Methods:
        safe_open(filepath: str, mode: str = 'r') -> Generator[TextIO, None, None]:
            Safely opens a file and yields a file object for use in a with statement.

    Raises:
        None: This class handles exceptions internally and ensures file closure.

    Example:
        >>> file_context = FileContext()
        >>> with file_context.safe_open('example.txt', 'w') as f:
        ...     f.write('Hello, World!')
        >>> # File is automatically closed after the with block
    """

    @contextmanager
    def safe_open(
        self, filepath: str, mode: str = "r"
    ) -> Generator[TextIO, None, None]:
        """
        Safely open and handle files using context manager.

        Args:
            filepath (str): Path to the file to be opened
            mode (str): File opening mode ('r', 'w', 'a', etc.)

        Yields:
            TextIO: File object that can be used in a with statement
        """
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        file = None
        try:
            file = open(filepath, mode)
            yield file
        finally:
            if file:
                file.close()
