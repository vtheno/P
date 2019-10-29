import logging
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
def exc_trace(exc):
    tb = exc.__traceback__
    """
    tb_frame
    tb_lasti
    tb_lineno
    tb_next
    """
    while tb.tb_next:
        tb = tb.tb_next
    frame = tb.tb_frame
    """
    f_code
    f_locals
    f_globals
    f_lineno
    ...
    """
    co = frame.f_code
    # print("[exception]", request, exc, tb)
    exc_lineno = frame.f_lineno
    exc_filename = co.co_filename
    exc_funcname = co.co_name
    exc_info = f"{exc_filename} [{exc_lineno}][{exc_funcname}] {type(exc)}:\n{exc}"
    return exc_info

def error(e: Exception):
    log.error("%s %s\n%s", type(e).__name__, e, exc_trace(e))