import logging
import subprocess
from pathlib import Path
from typing import Optional
from .models import UnitMetadata
from PyQt5.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)

class ProgramLauncher:
    """Helper class for launching external programs"""
    
    @staticmethod
    def launch_program(unit: UnitMetadata) -> Optional[subprocess.Popen]:
        """
        Launch a program specified in the unit's program_launch_info
        
        Args:
            unit: UnitMetadata containing program launch information
            
        Returns:
            subprocess.Popen object if launch successful, None otherwise
        """
        if not unit.program_launch_info:
            return None
            
        try:
            # Check if program is already running
            ps_cmd = ['pgrep', unit.program_launch_info.bin_name]
            result = subprocess.run(ps_cmd, capture_output=True)
            if result.returncode == 0:
                logger.info(f"Program {unit.program_launch_info.bin_name} is already running")
                return None

            cmd = [unit.program_launch_info.bin_name]
            
            # Add optional path if specified
            if unit.program_launch_info.path:
                path = Path(unit.program_launch_info.path)
                if path.exists():
                    cmd.append(str(path))
                    
            # Add optional arguments
            if unit.program_launch_info.args:
                cmd.extend(unit.program_launch_info.args)
                
            # Show confirmation dialog
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("Launch Program")
            msg.setText("The following program will be launched:")
            msg.setInformativeText(' '.join(cmd))
            msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            msg.setDefaultButton(QMessageBox.Ok)
            
            if msg.exec_() != QMessageBox.Ok:
                logger.info("Program launch cancelled by user")
                return None
                
            logger.info(f"Launching program: {' '.join(cmd)}")
            
            # Launch program as fully independent process
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,  # Create new session
                close_fds=True  # Close parent file descriptors
            )
            
            # Prevent zombie process by closing pipes
            process.stdout = None
            process.stderr = None
            
            return process
            
        except (subprocess.SubprocessError, FileNotFoundError) as e:
            logger.error(f"Failed to launch program: {e}")
            return None
