import subprocess
import logging
from pathlib import Path

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
                
            qm_file = ts_file.with_name(qm_name)
            
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

class CustomBuildHook:
    def initialize(self, version, build_data):
        """Compile .ts files to .qm files during build"""
        # Get the src directory path
        src_dir = Path(__file__).parent.parent
        
        # Compile all translations recursively
        compile_translations(src_dir)
