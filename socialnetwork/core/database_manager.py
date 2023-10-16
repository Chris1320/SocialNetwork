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
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                is_admin BOOLEAN NOT NULL,
                welcomed BOOLEAN NOT NULL
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS user_info (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                email TEXT,
                phone_number TEXT,
                address TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS friendships (
                user_id1 INTEGER, user_id2 INTEGER,
                PRIMARY KEY (user_id1, user_id2),
                FOREIGN KEY(user_id1) REFERENCES users(id),
                FOREIGN KEY(user_id2) REFERENCES users(id)
            )
            """
        )
