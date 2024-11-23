import subprocess
import logging
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logger = logging.getLogger(__name__)

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """No-op since translations are handled by Nix build"""
        pass
        
    def finalize(self, version, build_data, artifact_path):
        """No-op since translations are handled by Nix build"""
        pass
