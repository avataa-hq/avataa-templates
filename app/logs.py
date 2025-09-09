import logging
import logging.config

from config import ApplicationSettings


def conf_logging(conf: ApplicationSettings) -> None:
    lvl = logging.CRITICAL
    match conf.logging:
        case 50:
            lvl = logging.CRITICAL
        case 40:
            lvl = logging.ERROR
        case 30:
            lvl = logging.WARNING
        case 20:
            lvl = logging.INFO
        case 10:
            lvl = logging.DEBUG
    if conf.log_with_time:
        fmt = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    else:
        fmt = "%(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(level=lvl, format=fmt)
    logging.critical(f"SET {conf.logging} LEVEL")
