from uvicorn import run

from lib import api  # type: ignore[import]  # noqa: F401
from lib.app import app  # type: ignore[import]

if __name__ == '__main__':
    run(app)
