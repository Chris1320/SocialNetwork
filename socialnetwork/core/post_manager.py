from typing import Optional

from socialnetwork.core.database_manager import DatabaseManager


class PostManager(DatabaseManager):
    """
    This class handles all post-related operations.
    """

    def __init__(self) -> None:
        super().__init__()

    def post_message(self, user_id: int, message: str) -> None:
        """
        Post a message to the database.

        :param int user_id: The ID of the user who owns the post.
        :param str message: The message to post.
        """

        cursor = self.database.cursor()

        message = message.lstrip().rstrip()
        cursor.execute(
            "INSERT INTO posts (user_id, content) VALUES (?, ?);",
            (user_id, message),
        )

        self.database.commit()

    def get_posts(self, user_id: Optional[int] = None) -> list[dict[str, str]]:
        """
        Get all posts or posts of a specific user.

        :param Optional[int] user_id: The user ID, defaults to None
        :return list[dict[str,str]]: A list of posts.
        """

        cursor = self.database.cursor()

        if user_id is None:
            cursor.execute(
                """
                SELECT posts.id, users.username, posts.content, posts.timestamp
                FROM posts
                INNER JOIN users
                ON posts.user_id = users.id
                ORDER BY posts.timestamp DESC
                """
            )
        else:
            cursor.execute(
                """
                SELECT posts.id, users.username, posts.content, posts.timestamp
                FROM posts
                INNER JOIN users
                ON posts.user_id = users.id
                WHERE users.id = ?
                ORDER BY posts.timestamp DESC
                """,
                (user_id,),
            )

        posts = cursor.fetchall()

        return [
            {
                "id": post[0],
                "username": post[1],
                "content": post[2],
                "timestamp": post[3],
            }
            for post in posts
        ]
