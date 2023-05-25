#!/usr/bin/env python3
import yaml
import logging
from os import environ
from dotenv import load_dotenv
from os.path import isfile


class ConfigHelper:
    def __init__(self):
        self.configuration: any = None
        self._initialized: bool = False
        self.filename: str = None

    def initialize(self, filename: str | None = None, envfile: str = ".env", logger=None, ):
        try:
            # If filename is not given, try to get filename from environment. If that fails set it to None
            if filename is None:
                filename = environ.get("CONFIG", None)

            # If filename is still not given, try to load .env file. If environment ist still not set, set filename to None
            if filename is None:
                load_dotenv(envfile)
                filename = environ.get("CONFIG", None)

            # Check if ./config.yaml exists and load as default
            if filename is None:
                if isfile("./config.yaml"):
                    filename = "./config.yaml"

            # Config filename is none or does not exists? Kill devicenode service!
            if filename is None:
                raise Exception("Config filename is not definend")
            if not isfile(filename):
                raise Exception(f"Config filename '{filename}' does not exist")

            self.filename: str = filename
            self.error: bool = True
            if (logger is not None):
                self.logger = logger
            else:
                self.logger = logging.getLogger(__name__)
                self.logger.setLevel(logging.WARNING)

            self.load_config()

            self._initialized = True
        except Exception as e:
            print(f"Error: '{e}'")

    def load_config(self):
        try:
            with open(self.filename, "r") as fh:
                self.configuration = yaml.safe_load(fh)
                self.error = False
                fh.close()
        except Exception as e:
            self.logger.error(e)
            self.error = True

        return self.error

    def save_config(self):
        with open(self.filename, "w+") as f:
            yaml.dump(self.configuration, f)

    def get_var(self, name, default=None):
        ret = default

        try:
            name = name.lower()
            n = name.split(".")

            if len(n) == 1:
                ret = self.configuration[n[0]]
            elif len(n) == 2:
                ret = self.configuration[n[0]][n[1]]
            else:
                raise NameError(f"Yaml max depth is 2. Depth for '{name}' is {len(n)}")

        except NameError as e:
            self.logger.error(f"{type(e)}: {str(e)}'. Using default value '{default}'")
            ret = default
        except Exception as e:
            self.logger.error(
                f"{type(e)}: Couldn't read ConfigVar '{name}': '{str(e)}'. Using default value '{default}'"
            )
            ret = default

        return ret

    def get_varlist(self, category):
        varlist = []
        try:
            category = category.lower()
            varlist = self.configuration[category]
            pass
        except Exception as e:
            self.logger.error(
                f"{type(e)}: Couldn't read Category '{category}': '{str(e)}'."
            )

        self.logger.debug(f"varlist: '{varlist}'")
        return varlist


if __name__ == "__main__":
    # execute only if run as a script
    cf = ConfigHelper()
    cf.initialize("./src/cfghlp-test.yaml")

    print(cf.configuration)
    print("\r\nSections:")
    for section in cf.configuration:
        print(f" - {section}")
    print("\r\nTests:")
    print(f"category: {cf.configuration['category']}")
    print(f"logging level: {cf.configuration['logging']['level']}")
    print(f"mqtt port: {cf.get_var('mqtt.port')}")
    print(f"uns notinconfig: {cf.get_var('uns.NotInConfig')}")
