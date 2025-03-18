"""
Course publisher module for handling course publishing operations.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Tuple, Optional, List
import json

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
    
    @staticmethod
    def generate_ssh_key(key_name: str) -> Tuple[bool, str, str]:
        """
        Generate a new SSH key pair.
        
        Args:
            key_name: Name for the SSH key file
            
        Returns:
            Tuple[bool, str, str]: (success, public_key_path, error_message)
        """
        try:
            # Get the user's home directory
            home_dir = Path.home()
            ssh_dir = home_dir / ".ssh"
            
            # Create .ssh directory if it doesn't exist
            if not ssh_dir.exists():
                ssh_dir.mkdir(mode=0o700)
            
            # Generate key file paths
            key_path = ssh_dir / key_name
            pub_key_path = ssh_dir / f"{key_name}.pub"
            
            # Check if key already exists
            if key_path.exists() or pub_key_path.exists():
                return False, "", f"Key with name {key_name} already exists"
            
            # Generate SSH key
            result = subprocess.run(
                ["ssh-keygen", "-t", "ed25519", "-f", str(key_path), "-N", ""],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, "", f"Error generating SSH key: {result.stderr.strip()}"
            
            return True, str(pub_key_path), ""
        except Exception as e:
            logger.error(f"Error generating SSH key: {e}")
            return False, "", f"Error generating SSH key: {str(e)}"
    
    @staticmethod
    def create_remote_repository(ssh_pubkey: str, unit_name: str, username: str) -> Tuple[bool, str, str]:
        """
        Create a remote repository using the gitolite API.
        
        Args:
            ssh_pubkey: SSH public key content
            unit_name: Name of the unit/repository
            username: Username for the repository
            
        Returns:
            Tuple[bool, str, str]: (success, repo_url, error_message)
        """
        try:
            import requests
            from core.config import PortalConfig
            
            config = PortalConfig.load()
            api_url = config.gitolite_publish_api_url
            
            # Prepare request data
            data = {
                "ssh_pubkey": ssh_pubkey,
                "unit_name": unit_name,
                "username": username
            }
            
            # Send request to create repository
            response = requests.put(api_url + "/gitolite/repo", json=data)
            
            if response.status_code != 200:
                return False, "", f"Error creating repository: {response.text}"
            
            # Parse response
            result = response.json()
            repo_url = result.get("repo_url", "")
            message = result.get("message", "")
            
            if not repo_url:
                return False, "", f"No repository URL returned: {message}"
            
            return True, repo_url, message
        except Exception as e:
            logger.error(f"Error creating remote repository: {e}")
            return False, "", f"Error creating remote repository: {str(e)}"
    
    @staticmethod
    def setup_git_remote(directory: Path, remote_url: str) -> bool:
        """
        Set up a git remote for the repository.
        
        Args:
            directory: Path to the git repository
            remote_url: URL of the remote repository
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if remote already exists
            result = subprocess.run(
                ["git", "-C", str(directory), "remote"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if "origin" in result.stdout.split():
                # Remove existing origin remote
                subprocess.run(
                    ["git", "-C", str(directory), "remote", "remove", "origin"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False
                )
            
            # Add new origin remote
            result = subprocess.run(
                ["git", "-C", str(directory), "remote", "add", "origin", remote_url],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error setting up git remote: {e}")
            return False
    
    @staticmethod
    def push_to_remote(directory: Path, branch: str = "main") -> Tuple[bool, str]:
        """
        Push changes to the remote repository.
        
        Args:
            directory: Path to the git repository
            branch: Branch to push
            
        Returns:
            Tuple[bool, str]: (success, error_message)
        """
        try:
            # Push to remote
            result = subprocess.run(
                ["git", "-C", str(directory), "push", "-u", "origin", branch],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, result.stderr.strip()
            
            return True, ""
        except Exception as e:
            logger.error(f"Error pushing to remote: {e}")
            return False, str(e)
    
    @staticmethod
    def get_remote_url(directory: Path) -> Optional[str]:
        """
        Get the URL of the 'origin' remote for a git repository.
        
        Args:
            directory: Path to the git repository
            
        Returns:
            Optional[str]: The URL of the 'origin' remote, or None if not found
        """
        if not CoursePublisher.is_git_repository(directory):
            return None
            
        try:
            # Get the remote URL
            result = subprocess.run(
                ["git", "-C", str(directory), "remote", "get-url", "origin"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                # No remote or other error
                return None
                
            remote_url = result.stdout.strip()
            if remote_url:
                return remote_url
            
            return None
        except Exception as e:
            logger.error(f"Error getting remote URL: {e}")
            return None
