import os
import pathlib
from typing import Any, Dict

import yaml
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self):
        # Find the current directory (where this file is located)
        current_file = pathlib.Path(__file__).resolve()
        current_dir = current_file.parent
        # Load YAML config from the same directory as this file
        config_path = current_dir / "config.yaml"
        with open(config_path, "r") as f:
            self.yaml_config = yaml.safe_load(f)

        # Discord settings
        self.DISCORD_TOKEN = os.getenv("DISCORD_HILLBOT_TOKEN")
        self.DISCORD_CHARACTER_LIMIT = 2000

        # LLM settings
        self.LLM_MODEL = self.yaml_config["llm"]["model"]
        self.LLM_TEMPERATURE = self.yaml_config["llm"]["temperature"]
        self.LLM_MAX_TOKENS = self.yaml_config["llm"]["max_completion_tokens"]
        self.LLM_TOP_P = self.yaml_config["llm"]["top_p"]

        # Image generation settings
        self.IMAGE_MODEL = self.yaml_config["image_model"]["model"]
        self.IMAGE_SIZE = self.yaml_config["image_model"]["size"]
        self.IMAGE_RESPONSE_FORMAT = self.yaml_config["image_model"]["response_format"]

        # Variation settings
        self.VARIATION_MODEL = self.yaml_config["variation_model"]["model"]
        self.VARIATION_CFG = self.yaml_config["variation_model"]["cfg"]
        self.VARIATION_STEPS = self.yaml_config["variation_model"]["steps"]
        self.VARIATION_PROMPT_STRENGTH = self.yaml_config["variation_model"]["prompt_strength"]

        # Discord message history
        self.DISCORD_MESSAGE_LIMIT = self.yaml_config["discord"]["message_limit"]

    def get_discord_config(self) -> Dict[str, Any]:
        """Return Discord-specific configuration."""
        return {
            "token": self.DISCORD_TOKEN,
            "character_limit": self.DISCORD_CHARACTER_LIMIT,
            "message_limit": self.DISCORD_MESSAGE_LIMIT,
        }

    def get_llm_config(self) -> Dict[str, Any]:
        """Return LLM-specific configuration."""
        return {
            "model": self.LLM_MODEL,
            "temperature": self.LLM_TEMPERATURE,
            "max_tokens": self.LLM_MAX_TOKENS,
            "top_p": self.LLM_TOP_P,
        }

    def get_image_config(self) -> Dict[str, Any]:
        """Return image generation configuration."""
        return {
            "model": self.IMAGE_MODEL,
            "size": self.IMAGE_SIZE,
            "response_format": self.IMAGE_RESPONSE_FORMAT,
        }

    def get_variation_config(self) -> Dict[str, Any]:
        """Return image variation configuration."""
        return {
            "model": self.VARIATION_MODEL,
            "cfg": self.VARIATION_CFG,
            "steps": self.VARIATION_STEPS,
            "prompt_strength": self.VARIATION_PROMPT_STRENGTH,
        }


# Create a singleton instance
config = Config()
