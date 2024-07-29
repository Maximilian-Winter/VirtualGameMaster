import os
import json
from typing import Any, Dict
from dotenv import load_dotenv


class VirtualGameMasterConfig:
    def __init__(self):
        self.GAME_SAVE_FOLDER: str = ""
        self.INITIAL_GAME_STATE: str = ""
        self.MAX_MESSAGES: int = 0
        self.KEPT_MESSAGES: int = 0
        self.SYSTEM_MESSAGE_FILE: str = ""
        self.SAVE_SYSTEM_MESSAGE_FILE: str = ""
        self.MAX_TOKENS: int = 0
        self.API_TYPE: str = "openai"
        self.API_KEY: str | None = None
        self.API_URL: str = ""
        self.MODEL: str = ""
        self.TEMPERATURE: float = 0.7
        self.TOP_P: float = 1.0
        self.TOP_K: int = 0
        self.MIN_P: float = 0.0
        self.TFS_Z: float = 1.0
        self.COMMAND_PREFIX: str = "@"
        self.STOP_SEQUENCES: str = "[]"

    @classmethod
    def from_env(cls, env_file: str = ".env") -> "VirtualGameMasterConfig":
        load_dotenv(env_file)
        config = cls()
        config.GAME_SAVE_FOLDER = os.getenv("GAME_SAVE_FOLDER")
        config.INITIAL_GAME_STATE = os.getenv("INITIAL_GAME_STATE")
        config.MAX_MESSAGES = int(os.getenv("MAX_MESSAGES"))
        config.KEPT_MESSAGES = int(os.getenv("KEPT_MESSAGES"))
        config.SYSTEM_MESSAGE_FILE = os.getenv("SYSTEM_MESSAGE_FILE")
        config.SAVE_SYSTEM_MESSAGE_FILE = os.getenv("SAVE_SYSTEM_MESSAGE_FILE")
        config.MAX_TOKENS = int(os.getenv("MAX_TOKENS_PER_RESPONSE"))
        config.API_TYPE = os.getenv("API_TYPE", "openai").lower()
        config.API_KEY = os.getenv("API_KEY", None)
        config.API_URL = os.getenv("API_URL")
        config.MODEL = os.getenv("MODEL")
        config.TEMPERATURE = float(os.getenv("TEMPERATURE", 0.7))
        config.TOP_P = float(os.getenv("TOP_P", 1.0))
        config.TOP_K = int(os.getenv("TOP_K", 0))
        config.MIN_P = float(os.getenv("MIN_P", 0.0))
        config.TFS_Z = float(os.getenv("TFS_Z", 1.0))
        config.COMMAND_PREFIX = os.getenv("COMMAND_PREFIX", "@")
        config.STOP_SEQUENCES = os.getenv("STOP_SEQUENCES", "[]")
        return config

    @classmethod
    def from_json(cls, json_file: str) -> "VirtualGameMasterConfig":
        with open(json_file, "r") as f:
            data = json.load(f)
        config = cls()
        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, config._parse_value(key, value))
        return config

    def to_env(self, env_file: str = ".env") -> None:
        with open(env_file, "w") as f:
            for key, value in self.__dict__.items():
                f.write(f"{key}={value}\n")

    def to_json(self, json_file: str) -> None:
        with open(json_file, "w") as f:
            json.dump(self.__dict__, f, indent=2)

    def _parse_value(self, key: str, value: Any) -> Any:
        current_value = getattr(self, key)
        if isinstance(current_value, bool):
            return str(value).lower() in ("true", "1", "yes")
        if current_value is None:
            return value
        return type(current_value)(value)

    def update(self, updates: Dict[str, Any]) -> None:
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, self._parse_value(key, value))

    def to_dict(self) -> Dict[str, Any]:
        return {key: value for key, value in self.__dict__.items()}