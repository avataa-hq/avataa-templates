import logging
import logging.config

from config import ApplicationSettings


def conf_logging(conf: ApplicationSettings) -> None:
    lvl = logging.CRITICAL
    match conf.logging:
        case n if 41 <= n <= 50:
            lvl = logging.CRITICAL
        case n if 31 <= n <= 40:
            lvl = logging.ERROR
        case n if 21 <= n <= 30:
            lvl = logging.WARNING
        case n if 11 <= n <= 20:
            lvl = logging.INFO
        case n if 1 <= n <= 10:
            lvl = logging.DEBUG
    if conf.log_with_time:
        fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    else:
        fmt = "%(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(level=lvl, format=fmt)
    logging.critical(f"SET {logging.getLevelName(lvl)} LEVEL")
