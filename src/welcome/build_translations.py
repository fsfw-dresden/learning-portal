import subprocess
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Compile .ts files to .qm files during build"""
        translations_dir = Path(__file__).parent / "translations"
        
        # Ensure the translations directory exists
        translations_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all .ts files and compile them
        for ts_file in translations_dir.glob("*.ts"):
            qm_file = ts_file.with_suffix(".qm")
            try:
                subprocess.run(["lrelease", str(ts_file), "-qm", str(qm_file)], check=True)
                print(f"Compiled {ts_file.name} to {qm_file.name}")
            except subprocess.CalledProcessError as e:
                print(f"Error compiling {ts_file.name}: {e}")
                raise
            except FileNotFoundError:
                print("lrelease not found. Please install Qt Linguist tools.")
                raise
