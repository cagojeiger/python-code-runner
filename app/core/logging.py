import logging
import sys

import structlog
from structlog.processors import JSONRenderer, TimeStamper


def configure_logging(service: str, env: str, version: str) -> None:
    structlog.configure(
        processors=[
            TimeStamper(fmt="iso", utc=True),
            structlog.processors.add_log_level,
            JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    log = structlog.get_logger()
    log = log.bind(service=service, env=env, version=version)
