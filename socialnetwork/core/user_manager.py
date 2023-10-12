import hashlib
import random
from enum import Enum
from string import ascii_letters

from socialnetwork.core.database_manager import DatabaseManager


class UserLevel(Enum):
    ADMIN = 0
    NORMAL = 1


def validate_password(password: str) -> dict[str, bool | str]:
    """
    Validate a given password.

    :param str password: The password to validate.
    :return bool: True if the password is valid, False otherwise.
    """

    if len(password) < 8:
        return {"status": False, "message": "Password must be at least 8 characters."}

    return {"status": True, "message": "Password is valid."}


def hash_password(password: str, salt: str) -> str:
    """
    Hash the password and return its hex digest.

    :param str password: The password to hash.
    :returns: The hashed password.
    """

    return hashlib.sha256(":".join((salt, password, salt)).encode()).hexdigest()


class UserManager(DatabaseManager):
    """
    This class handles all user-related operations.
    """

    def __init__(self) -> None:
        super().__init__()

    def register_user(
        self, username: str, password: str, is_admin: bool = False
    ) -> None:
        """
        Register a new user in the database.

        Throws ValueError if the username already exists or the password is invalid.

        :param str username: The username of the user.
        :param str password: The password of the user.
        """

        cursor = self.database.cursor()

        # Check if the password is valid.
        password_validation = validate_password(password)
        if not password_validation["status"]:
            raise ValueError(password_validation["message"])

        # Check if the username is in the database.
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise ValueError("Username already exists.")

        # Hash the password.
        salt: str = "".join(random.choices(ascii_letters, k=16))
        password = hash_password(password, salt)

        cursor.execute(
            "INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
            (username, ":".join((password, salt)), is_admin),
        )
        self.database.commit()

    def validate_user(self, username: str, password: str) -> UserLevel:
        """
        Check if the username and their password is valid.

        :param str username: The username of the user.
        :param str password: The plaintext password of the user.
        :returns:
        """

        cursor = self.database.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        record = cursor.fetchone()
        if record is None:
            raise ValueError("Invalid username/password.")

        print(record)
        password = hash_password(password, record[2].partition(":")[2])

        if record[2].partition(":")[0] == password:
            return UserLevel.ADMIN if record[3] else UserLevel.NORMAL

        raise ValueError("Invalid username/password.")
