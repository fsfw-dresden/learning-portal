from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from core.compile_translations import compile_translations

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Compile .ts files to .qm files during build"""
        # Get the src directory path
        src_dir = Path(__file__).parent.parent
        
        # Compile all translations recursively
        compile_translations(src_dir)
