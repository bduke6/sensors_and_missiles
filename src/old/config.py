import os
import yaml

class Config:
    def __init__(self, config_path):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        with open(self.config_path, 'r') as file:
            try:
                self.config = yaml.safe_load(file)
            except yaml.YAMLError as exc:
                raise Exception(f"Error reading YAML file: {exc}")

        log_dir = self.get("environment.log_directory", "./logs")
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def get(self, key, default=None):
        keys = key.split(".")
        value = self.config
        try:
            for k in keys:
                value = value[k]
        except KeyError:
            if default is not None:
                return default
            raise KeyError(f"Configuration key '{key}' not found")
        return value

    def get_bool(self, key, default=False):
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1')
        return bool(value)
