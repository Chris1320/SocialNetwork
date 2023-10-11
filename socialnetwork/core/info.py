import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Server:
    host: str = "0.0.0.0"
    port: int = 5000
    debug: bool = True


@dataclass
class Brand:
    name: str = "Z"


@dataclass
class Filepath:
    html_templates: Path = Path(os.getcwd(), "www", "templates")
    static_files: Path = Path(os.getcwd(), "www", "static")
    media_files: Path = Path(os.getcwd(), "www", "media")
