import logging
from traceback import print_exception
FORMAT = "%(asctime)s [%(levelname)s][%(module)s][%(funcName)s]{%(lineno)d} %(message)s"
DATEFMT = '%Y-%m-%d %H:%M:%S %p'
logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt=DATEFMT)
DEBUG    = logging.DEBUG
INFO     = logging.INFO
WARNING  = logging.WARNING
ERROR    = logging.ERROR
CRITICAL = logging.CRITICAL
__all__ = ["log", "print", "info", "critical", "error", "warning"
           "DEBUG", "INFO", "CRITICAL", "ERROR", "WARNING" ]
log = logging.getLogger("")
print    = log.debug
info     = log.info
warnnig  = log.warning
critical = log.critical
def error(e: Exception):
    log.error("%s %s", type(e).__name__, e)
    # print_exception(type(e), e, e.__traceback__)
