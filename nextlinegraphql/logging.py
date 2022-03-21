import logging.config
from typing import Dict


def configure_logging(config: Dict):
    logging.config.dictConfig(config)

    # https://pypi.org/project/logging_tree/
    # import logging_tree
    # logging_tree.printout()
