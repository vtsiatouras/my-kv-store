import os
import logging
import logging.config
import coloredlogs
import yaml


def setup_logger(server: bool):

    try:
        os.makedirs("logs", exist_ok=True)
    except OSError as e:
        raise e

    # Some custom colors...
    coloredlogs.DEFAULT_LEVEL_STYLES = {
        "info": {"color": "white", "bold": False},
        "warning": {"color": 202, "bold": True},
        "error": {"color": 196, "bold": True},
    }
    coloredlogs.DEFAULT_FIELD_STYLES = {
        "asctime": {"color": "blue"},
        "levelname": {"color": "green"},
        "name": {"color": "cyan"},
    }

    if server:
        yaml_file = "server_logging_conf.yml"
    else:
        yaml_file = "broker_logging_conf.yml"

    with open("loggers/" + yaml_file, "rt") as f:
        config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
