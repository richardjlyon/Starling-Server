from config_path import ConfigPath

config_path = ConfigPath("starling_server", "rjlyon.com", ".json")
tokens_folder = config_path.saveFolderPath() / "tokens"
default_interval_days = 14
