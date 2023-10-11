from typing import Final

from flask import Flask

from socialnetwork.core import info
from socialnetwork.core import renderer

app: Final[Flask] = Flask(
    __name__,
    template_folder=info.Filepath.html_templates,
    static_folder=info.Filepath.static_files,
)


@app.route("/")
def index() -> str:
    return renderer.get_template("index.html")


@app.route("/login")
def login() -> str:
    return renderer.get_template("login.html")


@app.route("/register")
def register() -> str:
    return renderer.get_template("register.html")


if __name__ == "__main__":
    app.run(host=info.Server.host, port=info.Server.port, debug=info.Server.debug)
