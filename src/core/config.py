import os
from pathlib import Path
from typing import List, Optional
from dataclasses import dataclass
from venv import logger
from core.env_helper import EnvHelper
from dataclass_wizard import YAMLWizard
from platformdirs import site_config_dir

@dataclass
class PortalConfig(YAMLWizard):
    """Configuration for the Schulstick Portal"""
    unit_root_path: str  # Path to unit directory (relative or absolute)
    liascript_devserver: str = "http://localhost:3000"
    liascript_html_path: str = "/liascript/index.html"

    @classmethod
    def load(cls) -> 'PortalConfig':
        """Load config from appropriate location based on environment"""
        config_path = cls._get_config_path()
        

        logger.info(f"Config path: {config_path}")
        if not config_path.exists():
            logger.info(f"Config file does not exist, using default config")
            return cls.get_default_config()
            
        logger.info(f"Loading config from {config_path}")
        return cls.from_yaml_file(config_path)
    
    @staticmethod
    def _get_config_path() -> Path:
        """Get the appropriate config file path based on environment"""
        if EnvHelper.is_development():
            return Path('./dev_config/schulstick-portal-config.yml')
        else:
            config_dir = site_config_dir(appname='schulstick', multipath=True)
            return Path(config_dir) / 'schulstick-portal-config.yml'
    
    @classmethod
    def get_default_config(cls) -> 'PortalConfig':
        """Return default configuration"""
        return cls(
            unit_root_path='./tutor-next/markdown'
        )

    def save(self, path: Optional[Path] = None) -> None:
        """Save config to YAML file"""
        if path is None:
            path = self._get_config_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.to_yaml_file(path)
