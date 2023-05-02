from typing import Any, Optional
from loguru import logger


def logged(what, arg, log=logger.debug):
    log({what: arg})
    return arg


class NoneError(BaseException):
    """
    None encountered
    """


def NotNone(value: Optional[Any], description: Optional[str]):
    """
    Check for non-None value and raise an exeption with a description

    Args:
        value (Optional[Any]): Value to be checked for None
        description (Optional[str]): Description
    """
    if value is None:
        raise NoneError(description or "Unexpected None encountered")
