import sqlite3
from socialnetwork.core import info

class DatabaseManager:
    """
    This class manages the low-level database operations.
    """

    def __init__(self) -> None:
        self.database = sqlite3.connect(info.Filepath.database)

    def initialize_database(self) -> None:
        """
        Create the database.
        """

        self._create_users_table()

    def _create_users_table(self) -> None:
        """
        Create the users table.
        """

        cursor = self.database.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, password TEXT NOT NULL)")