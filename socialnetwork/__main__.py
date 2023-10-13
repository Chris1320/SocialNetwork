import logging
from time import strftime
from typing import Final

from flask import Flask, abort, flash, redirect, request, session, url_for
from werkzeug.wrappers import Response as WerkzeugResponse

from flask_session import Session
from socialnetwork.core import (
    database_manager,
    info,
    post_manager,
    renderer,
    user_manager,
)

# Set up the logger.
logger: Final[logging.Logger] = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if info.Server.debug else logging.INFO)
logger_handler: Final[logging.FileHandler] = logging.FileHandler(info.Filepath.logfile)
logger_handler.setLevel(logging.DEBUG if info.Server.debug else logging.INFO)
logger_formatter: Final[logging.Formatter] = logging.Formatter(info.Server.log_format)
logger_handler.setFormatter(logger_formatter)
logger.addHandler(logger_handler)

logger.info(f"Program started on {strftime('%Y-%m-%d %H:%M:%S')}")
app: Final[Flask] = Flask(
    __name__,
    template_folder=info.Filepath.html_templates,
    static_folder=info.Filepath.static_files,
)

# App and extension configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route("/favicon.ico")
def favicon() -> WerkzeugResponse:
    """
    Return the favicon.ico file.
    """

    return app.send_static_file("media/favicon.ico")


@app.route("/")
def index() -> str | WerkzeugResponse:
    """
    This route is the landing page, or newsfeed if the user is logged in.
    """

    if not session.get("logged_in"):
        return redirect(url_for("login"))

    server_message = request.args.get(
        "server_message",
        f"Welcome to {info.Brand.name}, {session.get('username')}!"
        if request.args.get("welcomed")
        else None,
    )

    posts: list[dict[str, str]] = post_manager.PostManager().get_posts()
    return renderer.get_template(
        "newsfeed.html",
        server_message=server_message,
        posts=posts,
    )


@app.route("/people")
def people() -> str | WerkzeugResponse:
    """
    Show the people page.
    """

    if not session.get("logged_in"):
        return redirect(url_for("index"))

    server_message = request.args.get(
        "server_message",
        None,
    )

    users = user_manager.UserManager().get_all_users()
    friends = user_manager.UserManager().get_friends_list(session["user_id"])
    users_with_friend_status: list[dict[str, str | bool]] = users.copy()  # type: ignore
    for idx, user in enumerate(users):
        users_with_friend_status[idx]["is_friend"] = (
            True if user["user_id"] in friends else False
        )
        users_with_friend_status[idx]["is_self"] = user["user_id"] == session["user_id"]

    return renderer.get_template(
        "people.html", users=users_with_friend_status, server_message=server_message
    )


@app.route("/people/add", methods=["GET"])
def add_friend() -> str | WerkzeugResponse:
    """
    Add a friend.
    """

    if not session.get("logged_in"):
        return abort(403)

    friend_id = int(request.args["friend_id"])
    user_manager.UserManager().friend_add(session["user_id"], friend_id)

    return redirect(url_for("people", server_message="Friend added!"))


@app.route("/people/remove", methods=["GET"])
def remove_friend() -> str | WerkzeugResponse:
    """
    Remove a friend.
    """

    if not session.get("logged_in"):
        return abort(403)

    friend_id = int(request.args["friend_id"])
    user_manager.UserManager().friend_remove(session["user_id"], friend_id)

    return redirect(url_for("people", server_message="Friend removed!"))


@app.route("/profile")
def profile() -> str | WerkzeugResponse:
    """
    Show the profile page of the user.
    """

    if not session.get("logged_in"):
        return redirect(url_for("index"))

    try:
        user_info: dict[str, str] = user_manager.UserManager().get_user_info(
            session["user_id"]
        )

    except ValueError:
        return redirect(url_for("welcome"))

    return renderer.get_template("profile.html", user_info=user_info)


@app.route("/about")
def about() -> str:
    """
    Show the about page of the site.
    """

    return renderer.get_template("about.html")


@app.route("/login", methods=["GET", "POST"])
def login() -> str | WerkzeugResponse:
    """
    Show the login form, or process the login form if it was POSTed.
    """

    if session.get("logged_in"):
        return redirect(url_for("index"))

    if request.method == "POST":
        try:
            username: str = request.form["username"]
            password: str = request.form["password"]
            user_id: int | None = user_manager.UserManager().validate_user(
                username=username, password=password
            )
            if user_id is not None:
                session["logged_in"] = True
                session["user_id"] = user_id
                session["username"] = username
                return redirect(url_for("index"))

            flash("Invalid username or password.")
            return renderer.get_template("login.html")

        except ValueError as error:
            flash(str(error))
            return renderer.get_template("login.html")

    return renderer.get_template("login.html")


@app.route("/logout")
def logout() -> WerkzeugResponse:
    """
    Log the user out.
    """

    session.pop("logged_in", None)
    session.pop("user_id", None)
    session.pop("username", None)

    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register() -> str | WerkzeugResponse:
    """
    Show the registration form, or process the registration form if it was POSTed.
    """

    if session.get("logged_in"):
        return redirect(url_for("index"))

    if request.method == "POST":
        username: str = request.form["username"]
        password: str = request.form["password"]
        password_confirm: str = request.form["password-confirm"]

        if password != password_confirm:
            flash("Passwords do not match.")
            return renderer.get_template("register.html")

        else:
            try:
                user_id: int = user_manager.UserManager().register_user(
                    username, password
                )
                if user_id is not None:
                    session["logged_in"] = True
                    session["user_id"] = user_id
                    session["username"] = username
                    user_manager.UserManager().update_user_info(session["user_id"], **request.form)
                    return redirect(url_for("index", welcomed=True))

            except ValueError as error:
                flash(str(error))
                return renderer.get_template("register.html")

    return renderer.get_template("register.html")


@app.route("/post", methods=["POST"])
def post() -> WerkzeugResponse:
    """
    Post a message.
    """

    if not session.get("logged_in"):
        return abort(403)

    message = request.form["message"]

    if len(message) > 140:
        return redirect(url_for("index", server_message="Message is too long!"))

    elif len(message) == 0:
        return redirect(url_for("index", server_message="Message is empty!"))

    post_manager.PostManager().post_message(session["user_id"], message)

    return redirect(url_for("index"))


@app.route("/admin", methods=["GET", "POST"])
def admin_dashboard() -> str | WerkzeugResponse:
    """
    Show the admin dashboard if the user is an admin. Otherwise, show form for inputting the admin_magic.
    """

    if not session.get("logged_in"):
        return redirect(url_for("index"))

    if request.method == "POST":
        if request.form["magic"] == info.Server.admin_magic:
            user_manager.UserManager().set_user_level(
                session["user_id"], user_manager.UserLevel.ADMIN
            )
            return redirect(url_for("admin_dashboard"))

        else:
            return redirect(
                url_for("admin_dashboard", server_message="Wrong admin magic!")
            )

    if (
        not user_manager.UserManager().get_user_level(session["user_id"])
        == user_manager.UserLevel.ADMIN
    ):
        return renderer.get_template("admin_magic.html")

    else:
        return renderer.get_template("admin_dashboard.html")


@app.route("/admin/demo/data/friendship", methods=["GET"])
def admin_friendship_dsa() -> str:
    """
    Show the adjacency matrix of the friendship graph.
    """

    if (
        not session.get("logged_in")
        or not user_manager.UserManager().get_user_level(session["user_id"])
        == user_manager.UserLevel.ADMIN
    ):
        return abort(403)

    users = user_manager.UserManager()._run("SELECT * FROM users")
    friendships = user_manager.UserManager()._run("SELECT * FROM friendships")

    # Create a matrix of all users, each record containing a value of 1 if the users are friends.
    matrix: list[list[int]] = [
        [0 for _ in range(len(users))] for _ in range(len(users))
    ]
    for friendship in friendships:
        matrix[friendship[0] - 1][friendship[1] - 1] = 1

    return renderer.get_template(
        "admin_friendship_dsa.html",
        col_length=range(len(matrix[0])),
        matrix=matrix,
        users=users,
    )


if __name__ == "__main__":
    # Prepare the database if it doesn't exist.
    if not info.Filepath.database.exists():
        logger.info("Database does not exist. Creating it now.")
        database_manager.DatabaseManager().initialize_database()

    logger.info("Starting the server.")
    app.run(host=info.Server.host, port=info.Server.port, debug=info.Server.debug)
