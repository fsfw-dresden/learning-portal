"""
Wizard for publishing courses to git repositories.
"""

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QHBoxLayout, QMessageBox,
    QComboBox, QRadioButton, QButtonGroup, QGroupBox,
    QDialog, QFileDialog, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path
import logging
import os

from core.models import Course
from portal.publish.course_publisher import CoursePublisher

logger = logging.getLogger(__name__)

def tr(text: str) -> str:
    """Helper function for translations"""
    from PyQt5.QtWidgets import QApplication
    return QApplication.translate("Portal", text)

class PublishIntroPage(QWizardPage):
    """Introduction page for the publish wizard"""
    
    def __init__(self, course: Course):
        super().__init__()
        self.course = course
        self.setTitle(tr("Publish Course"))
        self.setSubTitle(tr("This wizard will help you publish your course to a git repository."))
        
        layout = QVBoxLayout(self)
        
        # Course info
        course_info = QLabel(tr(f"Course: {course.title}"))
        layout.addWidget(course_info)
        
        # Git status
        self.status_label = QLabel()
        layout.addWidget(self.status_label)
        
        # SSH key info
        self.ssh_key_label = QLabel()
        layout.addWidget(self.ssh_key_label)
        
        # Update status when page is shown
        self.initializePage()
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        # Check git status
        if self.course.course_path:
            is_git, status_msg = CoursePublisher.get_git_status(self.course.course_path)
            self.status_label.setText(tr(f"Git Status: {status_msg}"))
        else:
            self.status_label.setText(tr("Course path not set"))
        
        # Check SSH keys
        ssh_keys = CoursePublisher.get_ssh_public_keys()
        if ssh_keys:
            self.ssh_key_label.setText(tr(f"Found {len(ssh_keys)} SSH key(s)"))
            # Store SSH keys in wizard field for later pages
            if hasattr(self.wizard(), 'ssh_keys'):
                self.wizard().ssh_keys = ssh_keys
        else:
            self.ssh_key_label.setText(tr("No SSH keys found. You will need to create one."))
            if hasattr(self.wizard(), 'ssh_keys'):
                self.wizard().ssh_keys = []

class SSHKeyPage(QWizardPage):
    """Page for managing SSH keys"""
    
    def __init__(self, course: Course):
        super().__init__()
        self.course = course
        self.setTitle(tr("SSH Key Management"))
        self.setSubTitle(tr("Select or create an SSH key for repository access"))
        
        layout = QVBoxLayout(self)
        
        # SSH key selection group
        self.key_group = QGroupBox(tr("SSH Key"))
        key_layout = QVBoxLayout(self.key_group)
        
        # Radio buttons for key options
        self.key_option_group = QButtonGroup(self)
        self.use_existing_radio = QRadioButton(tr("Use existing SSH key"))
        self.create_new_radio = QRadioButton(tr("Create new SSH key"))
        self.key_option_group.addButton(self.use_existing_radio)
        self.key_option_group.addButton(self.create_new_radio)
        
        key_layout.addWidget(self.use_existing_radio)
        
        # Existing key selection
        self.key_selection_layout = QHBoxLayout()
        self.key_combo = QComboBox()
        self.view_key_button = QPushButton(tr("View"))
        self.key_selection_layout.addWidget(self.key_combo)
        self.key_selection_layout.addWidget(self.view_key_button)
        key_layout.addLayout(self.key_selection_layout)
        
        # New key creation
        key_layout.addWidget(self.create_new_radio)
        self.new_key_layout = QHBoxLayout()
        self.key_name_input = QLineEdit()
        self.key_name_input.setPlaceholderText(tr("Enter key name (e.g. id_ed25519_course)"))
        self.new_key_layout.addWidget(self.key_name_input)
        key_layout.addLayout(self.new_key_layout)
        
        layout.addWidget(self.key_group)
        
        # Connect signals
        self.use_existing_radio.toggled.connect(self.update_key_ui)
        self.create_new_radio.toggled.connect(self.update_key_ui)
        self.view_key_button.clicked.connect(self.view_selected_key)
        
        # Register fields
        self.registerField("use_existing_key", self.use_existing_radio)
        self.registerField("key_name*", self.key_name_input)
        
        # Initialize UI state
        self.initializePage()
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        # Populate SSH key dropdown
        self.key_combo.clear()
        
        # Safely get ssh_keys from wizard
        ssh_keys = []
        if hasattr(self.wizard(), 'ssh_keys'):
            ssh_keys = self.wizard().ssh_keys
        else:
            # If ssh_keys not available, try to get them directly
            ssh_keys = CoursePublisher.get_ssh_public_keys()
            if hasattr(self.wizard(), 'ssh_keys'):
                self.wizard().ssh_keys = ssh_keys
        
        # Get the last used SSH key from config
        from core.config import PortalConfig
        config = PortalConfig.load()
        last_key_path = config.last_ssh_key_path
        last_key_index = -1
        
        # Add keys to dropdown
        for i, (key_path, _) in enumerate(ssh_keys):
            self.key_combo.addItem(os.path.basename(key_path), key_path)
            if key_path == last_key_path:
                last_key_index = i
        
        # Set initial radio button state based on available keys
        if ssh_keys:
            self.use_existing_radio.setChecked(True)
            self.create_new_radio.setChecked(False)
            
            # Select the last used key if available
            if last_key_index >= 0:
                self.key_combo.setCurrentIndex(last_key_index)
        else:
            self.use_existing_radio.setEnabled(False)
            self.create_new_radio.setChecked(True)
        
        self.update_key_ui()
    
    def update_key_ui(self):
        """Update UI based on selected key option"""
        use_existing = self.use_existing_radio.isChecked()
        
        # Enable/disable controls based on selection
        self.key_combo.setEnabled(use_existing)
        self.view_key_button.setEnabled(use_existing)
        self.key_name_input.setEnabled(not use_existing)
        
        # Update required fields
        if use_existing:
            self.key_name_input.setText("")
        else:
            # Suggest a default key name
            if not self.key_name_input.text():
                self.key_name_input.setText(f"id_ed25519_{self.course.title.lower().replace(' ', '_')}")
    
    def view_selected_key(self):
        """Show the selected SSH key content"""
        if self.key_combo.currentIndex() < 0:
            return
        
        key_path = self.key_combo.currentData()
        
        # Safely get ssh_keys from wizard
        ssh_keys = []
        if hasattr(self.wizard(), 'ssh_keys'):
            ssh_keys = self.wizard().ssh_keys
        else:
            # If ssh_keys not available, try to get them directly
            ssh_keys = CoursePublisher.get_ssh_public_keys()
        
        # Find the key content
        key_content = ""
        for path, content in ssh_keys:
            if path == key_path:
                key_content = content
                break
        
        if not key_content:
            return
        
        # Show key content in a dialog
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("SSH Public Key"))
        dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout(dialog)
        
        # Key content
        text_edit = QTextEdit()
        text_edit.setPlainText(key_content)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton(tr("Close"))
        close_button.clicked.connect(dialog.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def validatePage(self):
        """Validate the page before proceeding"""
        if self.create_new_radio.isChecked():
            # Generate new SSH key
            key_name = self.key_name_input.text()
            success, pub_key_path, error = CoursePublisher.generate_ssh_key(key_name)
            
            if not success:
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr(f"Failed to generate SSH key: {error}")
                )
                return False
            
            # Read the generated public key
            try:
                with open(pub_key_path, 'r') as f:
                    key_content = f.read().strip()
                
                # Add to the wizard's SSH keys
                if hasattr(self.wizard(), 'ssh_keys'):
                    self.wizard().ssh_keys.append((pub_key_path, key_content))
                if hasattr(self.wizard(), 'selected_key'):
                    self.wizard().selected_key = (pub_key_path, key_content)
                
                # Save the key path to config
                from core.config import PortalConfig
                config = PortalConfig.load()
                config.last_ssh_key_path = pub_key_path
                config.save()
                
                QMessageBox.information(
                    self,
                    tr("Success"),
                    tr(f"SSH key generated successfully: {pub_key_path}")
                )
                
                return True
            except Exception as e:
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr(f"Failed to read generated SSH key: {str(e)}")
                )
                return False
        else:
            # Use existing key
            if self.key_combo.currentIndex() < 0:
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr("Please select an SSH key")
                )
                return False
            
            key_path = self.key_combo.currentData()
            
            # Safely get ssh_keys from wizard
            ssh_keys = []
            if hasattr(self.wizard(), 'ssh_keys'):
                ssh_keys = self.wizard().ssh_keys
            else:
                # If ssh_keys not available, try to get them directly
                ssh_keys = CoursePublisher.get_ssh_public_keys()
            
            # Find the key content
            for path, content in ssh_keys:
                if path == key_path:
                    if hasattr(self.wizard(), 'selected_key'):
                        self.wizard().selected_key = (path, content)
                    
                    # Save the key path to config
                    from core.config import PortalConfig
                    config = PortalConfig.load()
                    config.last_ssh_key_path = path
                    config.save()
                    
                    return True
            
            QMessageBox.warning(
                self,
                tr("Error"),
                tr("Selected SSH key not found")
            )
            return False

class RepositorySetupPage(QWizardPage):
    """Page for setting up the repository"""
    
    def __init__(self, course: Course):
        super().__init__()
        self.course = course
        self.setTitle(tr("Repository Setup"))
        self.setSubTitle(tr("Configure your remote repository"))
        
        layout = QVBoxLayout(self)
        
        # Username
        layout.addWidget(QLabel(tr("Username:")))
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText(tr("Enter your username"))
        layout.addWidget(self.username_input)
        
        # Repository name
        layout.addWidget(QLabel(tr("Repository Name:")))
        self.repo_name_input = QLineEdit()
        self.repo_name_input.setPlaceholderText(tr("Enter repository name"))
        layout.addWidget(self.repo_name_input)
        
        # Register fields
        self.registerField("username*", self.username_input)
        self.registerField("repo_name*", self.repo_name_input)
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        # Suggest repository name based on course title
        if not self.repo_name_input.text():
            repo_name = self.course.title.lower().replace(' ', '-')
            self.repo_name_input.setText(repo_name)
        
        # Try to get username from environment
        if not self.username_input.text():
            username = os.environ.get('USER', '')
            self.username_input.setText(username)

class PublishOptionsPage(QWizardPage):
    """Page for configuring publish options"""
    
    def __init__(self, course: Course):
        super().__init__()
        self.course = course
        self.setTitle(tr("Publish Options"))
        self.setSubTitle(tr("Configure how you want to publish your course."))
        
        layout = QVBoxLayout(self)
        
        # Commit message
        layout.addWidget(QLabel(tr("Commit Message:")))
        self.commit_message = QLineEdit()
        self.commit_message.setText(tr(f"Update course: {course.title}"))
        layout.addWidget(self.commit_message)
        
        # Push to remote option
        self.push_checkbox = QCheckBox(tr("Push to remote repository"))
        self.push_checkbox.setChecked(True)
        layout.addWidget(self.push_checkbox)
        
        # Register fields
        self.registerField("commit_message*", self.commit_message)
        self.registerField("push_to_remote", self.push_checkbox)

class PublishSummaryPage(QWizardPage):
    """Summary page for the publish wizard"""
    
    def __init__(self, course: Course):
        super().__init__()
        self.course = course
        self.setTitle(tr("Publish Summary"))
        self.setSubTitle(tr("Review your publish settings before proceeding."))
        
        layout = QVBoxLayout(self)
        
        # Summary info
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        layout.addWidget(self.summary_label)
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        commit_message = self.field("commit_message")
        push_to_remote = self.field("push_to_remote")
        use_existing_key = self.field("use_existing_key")
        
        # Get SSH key info
        key_path = ""
        if hasattr(self.wizard(), "selected_key"):
            key_path = self.wizard().selected_key[0]
        
        # Get repository info
        username = self.field("username")
        repo_name = self.field("repo_name")
        
        summary = tr(f"Course: {self.course.title}\n\n")
        summary += tr(f"SSH Key: {os.path.basename(key_path)}\n")
        summary += tr(f"Username: {username}\n")
        summary += tr(f"Repository: {repo_name}\n\n")
        summary += tr(f"Commit Message: {commit_message}\n")
        summary += tr(f"Push to Remote: {'Yes' if push_to_remote else 'No'}")
        
        self.summary_label.setText(summary)

class PublishWizard(QWizard):
    """Wizard for publishing courses to git repositories"""
    
    publish_completed = pyqtSignal(bool, str)  # Success, message
    
    def __init__(self, course: Course, parent=None):
        super().__init__(parent)
        self.course = course
        self.ssh_keys = []  # Will be populated with available SSH keys
        self.selected_key = None  # Will store the selected or created key
        self.repo_url = None  # Will store the created repository URL
        
        self.setWindowTitle(tr("Publish Course"))
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Initialize pages
        intro_page = PublishIntroPage(course)
        ssh_key_page = SSHKeyPage(course)
        repo_setup_page = RepositorySetupPage(course)
        options_page = PublishOptionsPage(course)
        summary_page = PublishSummaryPage(course)
        
        # Add pages
        self.addPage(intro_page)
        self.addPage(ssh_key_page)
        self.addPage(repo_setup_page)
        self.addPage(options_page)
        self.addPage(summary_page)
        
        # Connect signals
        self.finished.connect(self.on_finished)
    
    def on_finished(self, result):
        """Handle wizard completion"""
        if result == QWizard.Accepted:
            # Get field values
            commit_message = self.field("commit_message")
            push_to_remote = self.field("push_to_remote")
            username = self.field("username")
            repo_name = self.field("repo_name")
            
            # Check if directory is a git repository
            is_git_repo = CoursePublisher.is_git_repository(self.course.course_path)
            
            if not is_git_repo:
                # Initialize git repository
                success = CoursePublisher.init_git_repository(self.course.course_path)
                if not success:
                    self.publish_completed.emit(False, tr("Failed to initialize git repository"))
                    return
            
            # Commit changes
            success = CoursePublisher.commit_changes(self.course.course_path, commit_message)
            if not success:
                self.publish_completed.emit(False, tr("Failed to commit changes"))
                return
            
            if push_to_remote:
                # Get SSH key content
                if not self.selected_key:
                    self.publish_completed.emit(False, tr("No SSH key selected"))
                    return
                
                _, key_content = self.selected_key
                
                # Create remote repository if needed
                if not self.repo_url:
                    success, repo_url, message = CoursePublisher.create_remote_repository(
                        key_content, repo_name, username
                    )
                    
                    if not success:
                        self.publish_completed.emit(False, tr(f"Failed to create repository: {message}"))
                        return
                    
                    self.repo_url = repo_url
                
                # Set up git remote
                success = CoursePublisher.setup_git_remote(self.course.course_path, self.repo_url)
                if not success:
                    self.publish_completed.emit(False, tr("Failed to set up git remote"))
                    return
                
                # Push to remote
                success, error = CoursePublisher.push_to_remote(self.course.course_path)
                if not success:
                    self.publish_completed.emit(False, tr(f"Failed to push to remote: {error}"))
                    return
                
                self.publish_completed.emit(True, tr(f"Course published successfully to {self.repo_url}"))
            else:
                self.publish_completed.emit(True, tr("Course changes committed successfully"))
