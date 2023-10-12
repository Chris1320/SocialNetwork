import logging
from time import strftime
from typing import Final

from flask import Flask, redirect, request, session, url_for
from werkzeug.wrappers import Response as WerkzeugResponse

from flask_session import Session
from socialnetwork.core import database_manager, info, renderer, user_manager

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
def index() -> str:
    """
    This route is the landing page, or newsfeed if the user is logged in.
    """

    # Check session if the user is already logged in.
    if not session.get("logged_in"):
        return renderer.get_template("index.html")

    return renderer.get_template(
        "newsfeed.html",
        server_message=f"Welcome to {info.Brand.name}, {session.get('username')}!"
            if request.args.get("welcomed")
            else None
    )


@app.route("/profile")
def profile() -> str | WerkzeugResponse:
    """
    Show the profile page of the user.
    """

    if not session.get('logged_in'):
        return redirect(url_for('index'))

    try:
        user_info: dict[str, str] = user_manager.UserManager().get_user_info(session["user_id"])

    except ValueError:
        return redirect(url_for('welcome'))

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

    if session.get('logged_in'):
        return redirect(url_for('index'))

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

            return renderer.get_template("login.html", error="Wrong username/password!")

        except ValueError as error:
            return renderer.get_template("login.html", error=str(error))

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

    if session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == "POST":
        username: str = request.form["username"]
        password: str = request.form["password"]
        password_confirm: str = request.form["password-confirm"]

        if password != password_confirm:
            return renderer.get_template(
                "register.html", error="Passwords do not match."
            )

        else:
            try:
                user_id: int = user_manager.UserManager().register_user(username, password)
                if user_id is not None:
                    session["logged_in"] = True
                    session["user_id"] = user_id
                    session["username"] = username
                    return redirect(url_for("welcome"))

            except ValueError as error:
                return renderer.get_template("register.html", error=str(error))

    return renderer.get_template("register.html")


@app.route("/welcome", methods=["GET", "POST"])
def welcome() -> str | WerkzeugResponse:
    """
    Show the welcome page, asking the user for their information.
    """

    if not session.get('logged_in'):
        return redirect(url_for('index'))

    if request.method == "POST":
        user_manager.UserManager().update_user_info(session["user_id"], **request.form)
        return redirect(url_for("index", welcomed=True))

    return renderer.get_template("welcome.html")


if __name__ == "__main__":
    # Prepare the database if it doesn't exist.
    if not info.Filepath.database.exists():
        logger.info("Database does not exist. Creating it now.")
        database_manager.DatabaseManager().initialize_database()

    logger.info("Starting the server.")
    app.run(host=info.Server.host, port=info.Server.port, debug=info.Server.debug)
