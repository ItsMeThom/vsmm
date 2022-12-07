import config
from os import getcwd

AppConfig = config.config_from_json(f"{getcwd()}/vsmm/config.json", read_from_file=True)