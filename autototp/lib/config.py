import os
from typing import Any

import yaml

from .util import NotNone

DEFAULT_UVICORN_RELOAD = 'false'


def config(name: str) -> Any:
    """
    Get configuration item

    Args:
        name (str): Config item name
    """
    return NotNone(
        yaml.safe_load(os.environ.get(f"AUTOTOTP_{name.upper()}", vars().get(f"DEFAULT_{name.upper()}", None))),
        f'Could not find a configuration value for {name}',
    )
