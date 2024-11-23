import subprocess
import logging
from pathlib import Path
from hatchling.builders.hooks.plugin.interface import BuildHookInterface

logger = logging.getLogger(__name__)

def compile_translations(base_dir: Path) -> None:
    """
    Compile all .ts files to .qm files recursively starting from base_dir
    
    Args:
        base_dir: Base directory to start searching for .ts files
    """
    # Find all translation directories
    translation_dirs = list(base_dir.rglob('translations'))
    
    if not translation_dirs:
        logger.warning(f"No translation directories found under {base_dir}")
        return
        
    for trans_dir in translation_dirs:
        # Ensure the translations directory exists
        trans_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all .ts files
        ts_files = list(trans_dir.glob('*.ts'))
        
        if not ts_files:
            logger.warning(f"No .ts files found in {trans_dir}")
            continue
            
        # Create translations directory in build output
        output_dir = trans_dir
        output_dir.mkdir(parents=True, exist_ok=True)
            
        # Compile each .ts file
        for ts_file in ts_files:
            # Get base name without extension
            base_name = ts_file.stem
            # Split on underscore to get language code if present
            parts = base_name.split('_')
            
            if len(parts) > 1:
                # If filename contains underscore, preserve the structure
                qm_name = f"{base_name}.qm"
            else:
                # Otherwise add module name prefix
                module_name = ts_file.parent.parent.name
                qm_name = f"{module_name}_{base_name}.qm"
                
            qm_file = output_dir / qm_name
            
            try:
                subprocess.run(
                    ["lrelease", str(ts_file), "-qm", str(qm_file)],
                    check=True,
                    capture_output=True,
                    text=True
                )
                logger.info(f"Compiled {ts_file.name} to {qm_file.name}")
            except subprocess.CalledProcessError as e:
                logger.error(f"Error compiling {ts_file.name}: {e.stderr}")
                raise
            except FileNotFoundError:
                logger.error("lrelease not found. Please install Qt Linguist tools.")
                raise

class CustomBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        """Compile .ts files to .qm files during build"""
        # Get the src directory path
        src_dir = Path(__file__).parent.parent
        
        # Compile all translations recursively
        compile_translations(src_dir)
        
    def finalize(self, version, build_data, artifact_path):
        """Ensure .qm files are included in the wheel"""
        # Get the src directory path
        src_dir = Path(__file__).parent.parent
        
        # Find all .qm files
        for qm_file in src_dir.rglob('*.qm'):
            # Get relative path from src dir
            rel_path = qm_file.relative_to(src_dir)
            # Copy to artifact using relative paths
            rel_path = qm_file.relative_to(src_dir)
            dest = Path(artifact_path) / rel_path
            dest.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(qm_file, dest)
