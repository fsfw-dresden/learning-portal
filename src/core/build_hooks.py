import os
import sys
from pathlib import Path
from .compile_translations import compile_translations

class CustomBuildHook:
    def initialize(self, version, build_data):
        """Compile .ts files to .qm files during build"""
        # Get the src directory path
        src_dir = Path(__file__).parent.parent
        
        # Compile all translations recursively
        compile_translations(src_dir)
