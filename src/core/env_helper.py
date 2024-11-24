import os
from enum import Enum

class Environment(Enum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"

class EnvHelper:
    @staticmethod
    def get_environment() -> Environment:
        """Get the current environment from SCHULSTICK_ENV"""
        env = os.getenv("SCHULSTICK_ENV", "development").lower()
        return Environment.PRODUCTION if env == "production" else Environment.DEVELOPMENT

    @staticmethod
    def is_production() -> bool:
        """Check if running in production environment"""
        return EnvHelper.get_environment() == Environment.PRODUCTION

    @staticmethod
    def is_development() -> bool:
        """Check if running in development environment"""
        return EnvHelper.get_environment() == Environment.DEVELOPMENT
