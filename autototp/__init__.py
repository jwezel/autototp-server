import better_exceptions

better_exceptions.hook()

try:
    import snoop  # type: ignore[import]

    snoop.install()
except Exception:
    pass

from .lib import api  # noqa: F401
from .lib.app import app  # noqa: F401
