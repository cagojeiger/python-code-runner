import os
import tomllib
from pathlib import Path


def get_project_version() -> str:
    pyproject_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    with pyproject_path.open("rb") as f:
        data = tomllib.load(f)
        return data["tool"]["poetry"]["version"]


SERVICE = os.getenv("SERVICE", "code-runner")
ENV = os.getenv("ENV", "dev")
VERSION = get_project_version()
