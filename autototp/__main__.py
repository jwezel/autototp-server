import better_exceptions

better_exceptions.hook()

try:
    import snoop  # type: ignore[import]

    snoop.install()
except Exception:
    pass

from lib import api  # type: ignore[import]  # noqa: F401
from lib.app import app  # type: ignore[import]  # noqa: F401
from lib.config import config  # type: ignore[import]
from uvicorn import run

if __name__ == '__main__':
    run('app:app', reload=config('UVICORN_RELOAD'))
