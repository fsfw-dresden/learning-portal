"""
Course publisher module for handling course publishing operations.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Tuple, Optional, List

logger = logging.getLogger(__name__)

class CoursePublisher:
    """Helper class for publishing courses to git repositories"""
    
    @staticmethod
    def is_git_repository(directory: Path) -> bool:
        """
        Check if the given directory is a git repository.
        
        Args:
            directory: Path to the directory to check
            
        Returns:
            bool: True if the directory is a git repository, False otherwise
        """
        try:
            # Check if the .git directory exists
            git_dir = directory / ".git"
            if git_dir.exists() and git_dir.is_dir():
                return True
                
            # Also check using git command
            result = subprocess.run(
                ["git", "-C", str(directory), "rev-parse", "--is-inside-work-tree"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except Exception as e:
            logger.error(f"Error checking if directory is a git repository: {e}")
            return False
    
    @staticmethod
    def get_git_status(directory: Path) -> Tuple[bool, str]:
        """
        Check if the git repository is clean (no uncommitted changes).
        
        Args:
            directory: Path to the git repository
            
        Returns:
            Tuple[bool, str]: (is_clean, status_message)
                - is_clean: True if the repository is clean, False otherwise
                - status_message: A message describing the status
        """
        if not CoursePublisher.is_git_repository(directory):
            return False, "Not a git repository"
            
        try:
            # Check for uncommitted changes
            result = subprocess.run(
                ["git", "-C", str(directory), "status", "--porcelain"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, f"Error running git status: {result.stderr.strip()}"
                
            if result.stdout.strip():
                # There are uncommitted changes
                return False, "Repository has uncommitted changes"
                
            # Check if we're behind/ahead of remote
            result = subprocess.run(
                ["git", "-C", str(directory), "status", "-sb"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            status_line = result.stdout.strip().split('\n')[0]
            
            if "ahead" in status_line:
                return False, "Repository has unpushed commits"
            elif "behind" in status_line:
                return False, "Repository is behind remote"
            elif "No commits yet" in status_line:
                return True, "Repository is clean (no commits yet)"
            else:
                return True, "Repository is clean and up to date"
                
        except Exception as e:
            logger.error(f"Error checking git status: {e}")
            return False, f"Error checking git status: {str(e)}"
    
    @staticmethod
    def init_git_repository(directory: Path) -> bool:
        """
        Initialize a new git repository in the given directory.
        
        Args:
            directory: Path to the directory to initialize
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ["git", "init", str(directory)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error initializing git repository: {e}")
            return False
    
    @staticmethod
    def commit_changes(directory: Path, message: str) -> bool:
        """
        Commit all changes in the repository.
        
        Args:
            directory: Path to the git repository
            message: Commit message
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not CoursePublisher.is_git_repository(directory):
            return False
            
        try:
            # Add all changes
            add_result = subprocess.run(
                ["git", "-C", str(directory), "add", "."],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if add_result.returncode != 0:
                logger.error(f"Error adding changes: {add_result.stderr.strip()}")
                return False
                
            # Commit changes
            commit_result = subprocess.run(
                ["git", "-C", str(directory), "commit", "-m", message],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            return commit_result.returncode == 0
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            return False
    
    @staticmethod
    def get_ssh_public_keys() -> List[Tuple[str, str]]:
        """
        Get a list of SSH public keys for the current user.
        
        Returns:
            List[Tuple[str, str]]: List of tuples containing (key_path, key_content)
        """
        try:
            # Get the user's home directory
            home_dir = Path.home()
            ssh_dir = home_dir / ".ssh"
            
            if not ssh_dir.exists() or not ssh_dir.is_dir():
                logger.warning(f"SSH directory not found: {ssh_dir}")
                return []
            
            # Find all public key files (*.pub)
            public_keys = []
            for file_path in ssh_dir.glob("*.pub"):
                try:
                    # Read the key content
                    with open(file_path, 'r') as f:
                        key_content = f.read().strip()
                    
                    # Add to the list
                    public_keys.append((str(file_path), key_content))
                except Exception as e:
                    logger.error(f"Error reading SSH key {file_path}: {e}")
            
            return public_keys
        except Exception as e:
            logger.error(f"Error getting SSH public keys: {e}")
            return []
