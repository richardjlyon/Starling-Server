__version__ = "0.1.0"

import pathlib

from config import config_from_yaml
from config_path import ConfigPath

ROOT = pathlib.Path(__file__).parent.absolute()
cfg = config_from_yaml(str(ROOT / "config.yaml"), read_from_file=True)

config_path = ConfigPath("starling_server", "rjlyon.com", ".json")
