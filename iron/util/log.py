#!/usr/bin/env python3

import logging
import coloredlogs

fmt = '[%(asctime)s,%(msecs)03d] [%(levelname)7s] [%(filename)s -- %(funcName)s():%(lineno)s] %(message)s'
coloredlogs.DEFAULT_FIELD_STYLES['levelname'] = {'bold': True}


def get_logger(name: str = None) -> logging.Logger:
    logger = logging.getLogger(name)
    coloredlogs.install(level=logging.INFO,
                        fmt=fmt,
                        milliseconds=True,
                        logger=logger)
    return logger
