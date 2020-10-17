import json
import os
import logging
import logging.handlers


class Settings:

    def __init__(self, config="config.json"):
        with open(config, encoding="utf_8") as f:
            data = json.load(f)
            self.TEACHERS = data["teachers"]
            self.REGEX = data["regex"]
            self.LOGIN = data["register"]["login"]
            self.PASSWORD = data["register"]["password"]
            self.DRIVER_NAME = data["driver"]["name"]
            self.DRIVER_PATH = os.path.join(os.path.abspath('.'), "drivers",
                                            data["driver"]["executable"])
            self.TOKEN: str = data["discord"]["token"]
            self.GUILD: str = data["discord"]["guild"]
            self.STATUS: str = data["discord"]["status"]
            self.GUILD_ID: int = int(data["discord"]["guild_id"])


settings = Settings()


def startLogging():
    log = logging.getLogger("libdisc")
    log.setLevel(logging.INFO)
    log_formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
    handler_stdout = logging.StreamHandler()
    handler_stdout.setFormatter(log_formatter)
    log.addHandler(handler_stdout)

    handler_file = logging.handlers.RotatingFileHandler("libdisc.log",
                                                        mode='a',
                                                        maxBytes=5 * 1024 *
                                                        1024,
                                                        backupCount=2)
    handler_file.setFormatter(log_formatter)
    log.addHandler(handler_file)
    return log


log = startLogging()