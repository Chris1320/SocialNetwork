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
    ) -> int:
        """
        Register a new user in the database.

        Throws ValueError if the username already exists or the password is invalid.

        :param str username: The username of the user.
        :param str password: The password of the user.
        :param bool is_admin: Whether the user is an admin or not.
        :returns: The user ID of the registered user.
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
            "INSERT INTO users (username, password, is_admin, welcomed) VALUES (?, ?, ?, ?)",
            (username, ":".join((password, salt)), is_admin, False),
        )
        self.database.commit()

        if cursor.lastrowid is None:
            raise ValueError("Failed to register user.")

        return cursor.lastrowid

    def get_user_info(self, user_id: int) -> dict[str, str]:
        """
        Get a user's information.

        :param int user_id: the user ID of the user.
        :return dict[str, str]: The row from the database containing the user's information.
        """

        cursor = self.database.cursor()

        cursor.execute("SELECT * FROM user_info WHERE user_id = ?", (user_id,))
        record = cursor.fetchone()
        if record is None:
            raise ValueError("User does not exist.")

        return {
            "first_name": record[1],
            "last_name": record[2],
            "email": record[3],
            "phone_number": record[4],
            "address": record[5],
        }

    def update_user_info(self, user_id: int, **kwargs) -> None:
        """
        Update the user's information.

        :param int user_id: The user ID of the user.
        """

        cursor = self.database.cursor()

        cursor.execute("SELECT * FROM user_info WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            cursor.execute(
                """
                UPDATE user_info
                SET first_name = ?, last_name = ?, email = ?, phone_number = ?, address = ?
                WHERE user_id = ?
                """,
                (
                    kwargs["first-name"],
                    kwargs["last-name"],
                    kwargs["email"],
                    kwargs["phone-number"],
                    kwargs["address"],
                    user_id,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO user_info
                (user_id, first_name, last_name, email, phone_number, address)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    user_id,
                    kwargs["first-name"],
                    kwargs["last-name"],
                    kwargs["email"],
                    kwargs["phone-number"],
                    kwargs["address"],
                ),
            )

        cursor.execute("UPDATE users SET welcomed = ? WHERE id = ?", (True, user_id))
        self.database.commit()

    def validate_user(self, username: str, password: str) -> int | None:
        """
        Check if the username and their password is valid.

        :param str username: The username of the user.
        :param str password: The plaintext password of the user.
        :returns: The user ID if the username and password is valid, None otherwise.
        """

        cursor = self.database.cursor()

        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        record = cursor.fetchone()
        if record is None:
            raise ValueError("Invalid username/password.")

        print(record)
        password = hash_password(password, record[2].partition(":")[2])

        if record[2].partition(":")[0] == password:
            return record[0]

        raise ValueError("Invalid username/password.")
