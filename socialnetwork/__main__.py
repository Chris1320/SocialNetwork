import logging
from time import strftime
from typing import Final

from flask import Flask, request

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


@app.route("/")
def index() -> str:
    return renderer.get_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login() -> str:
    if request.method == "POST":
        try:
            username: str = request.form["username"]
            password: str = request.form["password"]
            if user_manager.UserManager().validate_user(username=username, password=password):
                return renderer.get_template("newsfeed.html")
            
            return renderer.get_template("login.html", error="Wrong username/password!")

        except ValueError as error:
            return renderer.get_template("login.html", error=str(error))

    return renderer.get_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register() -> str:
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
                user_manager.UserManager().register_user(username, password)
                return renderer.get_template("index.html", server_message="User created.")

            except ValueError as error:
                return renderer.get_template("register.html", error=str(error))

    return renderer.get_template("register.html")


if __name__ == "__main__":
    # Prepare the database if it doesn't exist.
    if not info.Filepath.database.exists():
        logger.info("Database does not exist. Creating it now.")
        database_manager.DatabaseManager().initialize_database()

    logger.info("Starting the server.")
    app.run(host=info.Server.host, port=info.Server.port, debug=info.Server.debug)
