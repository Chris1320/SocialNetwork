import os
from pathlib import Path


class Server:
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True
    log_format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s" 


class Brand:
    name: str = "Da Peysbuk"


class Filepath:
    database: Path = Path(os.getcwd(), "socialnetwork.db")
    logfile: Path = Path(os.getcwd(), "socialnetwork.log")
    html_templates: Path = Path(os.getcwd(), "www", "templates")
    static_files: Path = Path(os.getcwd(), "www", "static")
    media_files: Path = Path(os.getcwd(), "www", "media")
