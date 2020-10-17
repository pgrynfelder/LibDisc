import json
import os


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
            self.TOKEN = config["discord"]["token"]
            self.GUILD = config["discord"]["guild"]
            self.GUILD_ID = config["discord"]["guild_id"]


settings = Settings()