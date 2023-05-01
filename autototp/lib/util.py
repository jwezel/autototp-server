from loguru import logger


def logged(what, arg, log=logger.debug):
    log({what: arg})
    return arg
