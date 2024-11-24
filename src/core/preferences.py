from dataclasses import dataclass, asdict, field
from enum import Enum
from pathlib import Path
import yaml
from platformdirs import user_config_dir
from core.env_helper import EnvHelper

APP_NAME = "vision-assistant"

@dataclass
class SkillLevelPreferences:
    """User skill level preferences"""
    grade: int = 1
    age: int = 6
    subjects: dict[str, int] = field(default_factory=lambda: {
        "german": 1,
        "foreign_language": 1,
        "mathematics": 1,
        "computer_science": 1,
        "natural_science": 1
    })

class Gender(Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"

supported_locales = ["de_DE", "en_US"]

@dataclass
class ApplicationSupportPreferences:
    """Application support preferences"""
    welcome_wizard_finished: bool = False


@dataclass
class UserPreferences:
    """User identity preferences"""
    nick: str = "Anonymous"
    avatar: str = "default.png"
    locale: str = "de_DE"
    gender: Gender = Gender.OTHER


@dataclass
class Preferences:
    """Combined user preferences"""
    skill: SkillLevelPreferences = field(default_factory=SkillLevelPreferences)
    user: UserPreferences = field(default_factory=UserPreferences)
    support: ApplicationSupportPreferences = field(default_factory=ApplicationSupportPreferences)
    
    @classmethod
    def load(cls) -> 'Preferences':
        """Load preferences from YAML file"""
        config_path = cls._get_config_path()
        
        if not config_path.exists():
            # Return default preferences if no config exists
            return cls()
            
        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
            
        if not data:
            return cls()
            
        return cls(
            skill=SkillLevelPreferences(**data.get('skill', {})),
            user=UserPreferences(**data.get('user', {})),
            support=ApplicationSupportPreferences(**data.get('support', {}))
        )

    def save(self) -> None:
        """Save preferences to YAML file"""
        config_path = self._get_config_path()
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            yaml.dump(asdict(self), f)

    @staticmethod
    def _get_config_path() -> Path:
        """Get the appropriate config file path based on environment"""
        if EnvHelper.is_development():
            return Path("dev_config/preferences.yml")
        return Path(user_config_dir(APP_NAME)) / "preferences.yml"
