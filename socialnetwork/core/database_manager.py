import sqlite3

from socialnetwork.core import info


class DatabaseManager:
    """
    This class contains the low-level database operations, and
    serves as a base class for other classes that need to interact
    with the database.
    """

    def __init__(self) -> None:
        self.database = sqlite3.connect(info.Filepath.database)

    def initialize_database(self) -> None:
        """
        Create the database.
        """

        cursor = self.database.cursor()
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT NOT NULL, password TEXT NOT NULL)"
        )
