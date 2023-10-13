import os
from pathlib import Path


class Brand:
    name: str = "Social Network"


class Filepath:
    database: Path = Path(os.getcwd(), "socialnetwork.db")
    logfile: Path = Path(os.getcwd(), "socialnetwork.log")
    html_templates: Path = Path(os.getcwd(), "www", "templates")
    static_files: Path = Path(os.getcwd(), "www", "static")
    media_files: Path = Path(os.getcwd(), "www", "media")
    admin_magic: Path = Path(os.getcwd(), "admin_magic.txt")


class Server:
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True
    log_format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    with open(Filepath.admin_magic, 'r') as fopen:
        admin_magic: str = fopen.readline().lstrip().rstrip()
