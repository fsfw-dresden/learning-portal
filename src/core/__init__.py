from core.preferences import Preferences, SkillLevelPreferences, UserPreferences
from core.env_helper import Environment, EnvHelper
from core.compile_translations import compile_translations

# Only import build hooks when needed
try:
    from core.build_hooks import CustomBuildHook
except ImportError:
    pass
