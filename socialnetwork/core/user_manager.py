import hashlib

from socialnetwork.core.database_manager import DatabaseManager


def validate_password(password: str) -> dict[str, bool | str]:
    """
    Validate a given password.

    :param str password: The password to validate.
    :return bool: True if the password is valid, False otherwise.
    """

    if len(password) < 8:
        return {"status": False, "message": "Password must be at least 8 characters."}

    return {"status": True, "message": "Password is valid."}


class UserManager(DatabaseManager):
    """
    This class handles all user-related operations.
    """

    def __init__(self) -> None:
        super().__init__()

    def register_user(self, username: str, password: str) -> None:
        """
        Register a new user in the database.

        Throws ValueError if the username already exists or the password is invalid.

        :param str username: The username of the user.
        :param str password: The password of the user.
        """

        cursor = self.database.cursor()

        # Check if the username is in the database.
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            raise ValueError("Username already exists.")

        # Check if the password is valid.
        password_validation = validate_password(password)
        if not password_validation["status"]:
            raise ValueError(password_validation["message"])

        # Hash the password. (without salt)
        password = hashlib.sha256(password.encode()).hexdigest()

        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)", (username, password)
        )
        self.database.commit()
