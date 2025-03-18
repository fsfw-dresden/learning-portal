"""
Wizard for publishing courses to git repositories.
"""

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QHBoxLayout, QMessageBox,
    QComboBox, QRadioButton, QButtonGroup, QGroupBox,
    QDialog, QTextEdit, QProgressBar
)
from PyQt5.QtCore import pyqtSignal, QThread
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
        
        # Add explanation about simplified vs extended publish
        explanation = QLabel(tr("You can choose between:"))
        explanation.setWordWrap(True)
        layout.addWidget(explanation)
        
        # Quick publish option
        quick_publish_info = QLabel(tr("• Quick Publish: Immediately publish with default settings"))
        quick_publish_info.setWordWrap(True)
        layout.addWidget(quick_publish_info)
        
        # Extended publish option
        extended_publish_info = QLabel(tr("• Extended Publish: Configure all publishing options step by step"))
        extended_publish_info.setWordWrap(True)
        layout.addWidget(extended_publish_info)
        
        # Add spacer
        layout.addSpacing(20)
        
        # Quick publish button
        self.quick_publish_button = QPushButton(tr("Quick Publish"))
        self.quick_publish_button.setMinimumHeight(50)  # Make the button bigger
        self.quick_publish_button.setStyleSheet("font-weight: bold;")
        self.quick_publish_button.clicked.connect(self.on_quick_publish)
        layout.addWidget(self.quick_publish_button)
        
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
    
    def on_quick_publish(self):
        """Handle quick publish button click"""
        wizard = self.wizard()
        
        # Disable the button immediately
        self.quick_publish_button.setEnabled(False)
        self.quick_publish_button.setText(tr("Publishing..."))
        
        # Create progress dialog
        progress_dialog = QDialog(self)
        progress_dialog.setWindowTitle(tr("Publishing Course"))
        progress_dialog.setMinimumWidth(400)
        progress_dialog.setModal(True)
        
        dialog_layout = QVBoxLayout(progress_dialog)
        
        # Status label
        status_label = QLabel(tr("Preparing to publish..."))
        status_label.setWordWrap(True)
        dialog_layout.addWidget(status_label)
        
        # Progress bar (indeterminate)
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 0)  # Indeterminate
        dialog_layout.addWidget(progress_bar)
        
        # Abort button
        button_layout = QHBoxLayout()
        abort_button = QPushButton(tr("Abort"))
        button_layout.addStretch()
        button_layout.addWidget(abort_button)
        dialog_layout.addLayout(button_layout)
        
        # 1. Check/create SSH key
        ssh_keys = []
        if hasattr(wizard, 'ssh_keys'):
            ssh_keys = wizard.ssh_keys
        
        # Get the preferred SSH key from config
        from core.preferences import Preferences
        preferences = Preferences.load()
        preferred_key_path = preferences.course_publish.default_ssh_pubkey
        
        key_path = None
        key_content = None
        
        if ssh_keys:
            # Try to use preferred key first
            for path, content in ssh_keys:
                if path == preferred_key_path:
                    key_path = path
                    key_content = content
                    break
            
            # If no preferred key found, use the first one
            if not key_path and ssh_keys:
                key_path, key_content = ssh_keys[0]
        
        # If no keys exist, generate one
        if not key_path:
            status_label.setText(tr("Generating SSH key..."))
            progress_dialog.show()
            QApplication.processEvents()
            
            # Generate default key name based on course
            key_name = f"id_ed25519_{self.course.title.lower().replace(' ', '_')}"
            success, pub_key_path, error = CoursePublisher.generate_ssh_key(key_name)
            
            if not success:
                progress_dialog.close()
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr(f"Failed to generate SSH key: {error}")
                )
                self.quick_publish_button.setEnabled(True)
                self.quick_publish_button.setText(tr("Quick Publish"))
                return
            
            # Read the generated public key
            try:
                with open(pub_key_path, 'r') as f:
                    key_content = f.read().strip()
                
                key_path = pub_key_path
                
                # Save as preferred key
                preferences.course_publish.default_ssh_pubkey = pub_key_path
                preferences.save()
            except Exception as e:
                progress_dialog.close()
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr(f"Failed to read generated SSH key: {str(e)}")
                )
                self.quick_publish_button.setEnabled(True)
                self.quick_publish_button.setText(tr("Quick Publish"))
                return
        
        # Store the selected key
        if hasattr(wizard, 'selected_key'):
            wizard.selected_key = (key_path, key_content)
        
        # 2. Set default repository info
        username = os.environ.get('USER', '')
        repo_name = self.course.title.lower().replace(' ', '-')
        
        # Create and start the worker thread
        self.publish_worker = PublishWorker(
            self.course, key_path, key_content, username, repo_name
        )
        
        # Connect signals
        self.publish_worker.progress_update.connect(status_label.setText)
        self.publish_worker.operation_complete.connect(self.on_publish_complete)
        abort_button.clicked.connect(self.publish_worker.abort)
        
        # Show dialog and start worker
        progress_dialog.show()
        self.progress_dialog = progress_dialog  # Store reference to prevent garbage collection
        self.publish_worker.start()

    def on_publish_complete(self, success, message, repo_url):
        """Handle completion of the publish operation"""
        # Close the progress dialog
        if hasattr(self, 'progress_dialog') and self.progress_dialog:
            self.progress_dialog.close()
        
        # Re-enable the button
        self.quick_publish_button.setEnabled(True)
        self.quick_publish_button.setText(tr("Quick Publish"))
        
        # Show result message
        if success:
            QMessageBox.information(
                self,
                tr("Success"),
                tr(f"Course published successfully to {repo_url}")
            )
            
            # Emit the publish_completed signal
            wizard = self.wizard()
            if hasattr(wizard, 'publish_completed'):
                wizard.publish_completed.emit(True, tr(f"Course published successfully to {repo_url}"))
            
            # Close the wizard
            wizard.accept()
        else:
            QMessageBox.warning(
                self,
                tr("Error"),
                message
            )

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
        self.key_combo.currentIndexChanged.connect(self.on_key_selected)
        
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
        from core.preferences import Preferences
        preferences = Preferences.load()
        last_key_path = preferences.course_publish.default_ssh_pubkey
        last_key_index = -1
        
        # Add keys to dropdown
        for i, (key_path, content) in enumerate(ssh_keys):
            self.key_combo.addItem(os.path.basename(key_path), key_path)
            if key_path == last_key_path:
                last_key_index = i
                # Pre-select this key in the wizard
                if hasattr(self.wizard(), 'selected_key'):
                    self.wizard().selected_key = (key_path, content)
        
        # Set initial radio button state based on available keys
        if ssh_keys:
            self.use_existing_radio.setChecked(True)
            self.create_new_radio.setChecked(False)
            
            # Select the last used key if available
            if last_key_index >= 0:
                self.key_combo.setCurrentIndex(last_key_index)
            elif len(ssh_keys) > 0:
                # If no last key but we have keys, select the first one
                self.key_combo.setCurrentIndex(0)
                key_path, content = ssh_keys[0]
                if hasattr(self.wizard(), 'selected_key'):
                    self.wizard().selected_key = (key_path, content)
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
            
            # Update selected key when radio button changes
            if self.key_combo.currentIndex() >= 0:
                key_path = self.key_combo.currentData()
                
                # Find the key content
                ssh_keys = []
                if hasattr(self.wizard(), 'ssh_keys'):
                    ssh_keys = self.wizard().ssh_keys
                else:
                    ssh_keys = CoursePublisher.get_ssh_public_keys()
                
                for path, content in ssh_keys:
                    if path == key_path:
                        if hasattr(self.wizard(), 'selected_key'):
                            self.wizard().selected_key = (path, content)
                        break
        else:
            # Suggest a default key name
            if not self.key_name_input.text():
                self.key_name_input.setText(f"id_ed25519_{self.course.title.lower().replace(' ', '_')}")
    
    def on_key_selected(self, index):
        """Handle selection of a key from the dropdown"""
        if index < 0:
            return
            
        key_path = self.key_combo.currentData()
        
        # Safely get ssh_keys from wizard
        ssh_keys = []
        if hasattr(self.wizard(), 'ssh_keys'):
            ssh_keys = self.wizard().ssh_keys
        else:
            # If ssh_keys not available, try to get them directly
            ssh_keys = CoursePublisher.get_ssh_public_keys()
        
        # Find the key content and update selected_key
        for path, content in ssh_keys:
            if path == key_path:
                if hasattr(self.wizard(), 'selected_key'):
                    self.wizard().selected_key = (path, content)
                break
    
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
    
    def isComplete(self) -> bool:
        """Always return True to enable the Next button"""
        return True

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
                from core.preferences import Preferences
                preferences = Preferences.load()
                preferences.course_publish.default_ssh_pubkey = pub_key_path
                preferences.save()
                
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
            key_found = False
            for path, content in ssh_keys:
                if path == key_path:
                    if hasattr(self.wizard(), 'selected_key'):
                        self.wizard().selected_key = (path, content)
                    
                    # Save the key path to config
                    from core.preferences import Preferences
                    preferences = Preferences.load()
                    preferences.course_publish.default_ssh_pubkey = path
                    preferences.save()
                    
                    key_found = True
                    break
            
            if not key_found:
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr("Selected SSH key not found")
                )
                return True
            
            return True

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
        
        # Remote repository section
        remote_group = QGroupBox(tr("Remote Repository"))
        remote_layout = QVBoxLayout(remote_group)
        
        # Existing remote info
        self.remote_info_label = QLabel()
        self.remote_info_label.setWordWrap(True)
        remote_layout.addWidget(self.remote_info_label)
        
        # Remote URL edit
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel(tr("Remote URL:")))
        self.remote_url_edit = QLineEdit()
        url_layout.addWidget(self.remote_url_edit)
        remote_layout.addLayout(url_layout)
        
        # Create repository button
        button_layout = QHBoxLayout()
        self.create_repo_button = QPushButton(tr("Create Repository"))
        self.create_repo_button.clicked.connect(self.create_repository)
        button_layout.addWidget(self.create_repo_button)
        button_layout.addStretch()
        remote_layout.addLayout(button_layout)
        
        layout.addWidget(remote_group)
        
        # Push to remote option
        self.push_checkbox = QCheckBox(tr("Push to remote repository"))
        self.push_checkbox.setChecked(True)
        layout.addWidget(self.push_checkbox)
        
        # Register fields
        self.registerField("commit_message*", self.commit_message)
        self.registerField("push_to_remote", self.push_checkbox)
        self.registerField("remote_url", self.remote_url_edit)
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        # Check for existing remote
        existing_remote = None
        if self.course.course_path:
            existing_remote = CoursePublisher.get_remote_url(self.course.course_path)
        
        # Get repository info from previous pages
        username = self.field("username")
        repo_name = self.field("repo_name")
        
        # Set remote URL info and field
        if existing_remote:
            self.remote_url_edit.setText(existing_remote)
            self.create_repo_button.setEnabled(False)
            self.create_repo_button.setText(tr("Repository Already Exists"))
        else:
            # If we have a repo_url from a previous step, use that
            if hasattr(self.wizard(), 'repo_url') and self.wizard().repo_url:
                expected_url = self.wizard().repo_url
                self.remote_info_label.setText(tr("Repository has been created."))
                self.create_repo_button.setEnabled(False)
                self.create_repo_button.setText(tr("Repository Already Created"))
            else:
                # Generate expected remote URL based on username and repo_name
                # This is just a placeholder - the actual URL format depends on your git server
                expected_url = f"git@git.example.com:{username}/{repo_name}.git"
                self.remote_info_label.setText(tr("No existing remote URL detected. You can create a new repository."))
                self.create_repo_button.setEnabled(True)
            
            self.remote_url_edit.setText(expected_url)
    
    def create_repository(self):
        """Create a new repository using the CoursePublisher"""
        # Get SSH key content
        if not hasattr(self.wizard(), 'selected_key') or not self.wizard().selected_key:
            QMessageBox.warning(
                self,
                tr("Error"),
                tr("No SSH key selected. Please go back and select or create an SSH key.")
            )
            return
        
        _, key_content = self.wizard().selected_key
        
        # Get repository info
        username = self.field("username")
        repo_name = self.field("repo_name")
        
        # Create the repository
        success, repo_url, message = CoursePublisher.create_remote_repository(
            key_content, repo_name, username
        )
        
        if not success:
            QMessageBox.warning(
                self,
                tr("Error"),
                tr(f"Failed to create repository: {message}")
            )
            return
        
        # Update UI
        self.remote_info_label.setText(tr("Repository created successfully."))
        self.remote_url_edit.setText(repo_url)
        self.create_repo_button.setEnabled(False)
        self.create_repo_button.setText(tr("Repository Created"))
        
        # Store the repo URL in the wizard
        if hasattr(self.wizard(), 'repo_url'):
            self.wizard().repo_url = repo_url
        
        QMessageBox.information(
            self,
            tr("Success"),
            tr(f"Repository created successfully: {repo_url}")
        )
    
    def validatePage(self):
        """Validate the page before proceeding"""
        # Update the repo_url in the wizard with the possibly edited value
        if hasattr(self.wizard(), 'repo_url'):
            self.wizard().repo_url = self.remote_url_edit.text()
        return True
    
    def isComplete(self) -> bool:
        """Always return True to enable the Finish button"""
        return True

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
        
        # Register a dummy field to make the page complete
        self.registerField("summary_complete", self.summary_label)
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        commit_message = self.field("commit_message")
        push_to_remote = self.field("push_to_remote")
        use_existing_key = self.field("use_existing_key")
        
        # Get SSH key info
        key_path = ""
        if hasattr(self.wizard(), "selected_key") and self.wizard().selected_key:
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
    
    def isComplete(self) -> bool:
        """Always return True to enable the Finish button"""
        return True

# Add this new class for the background worker
class PublishWorker(QThread):
    """Worker thread for publishing courses in the background"""
    
    # Signals for progress updates and completion
    progress_update = pyqtSignal(str)
    operation_complete = pyqtSignal(bool, str, str)  # Success, message, repo_url
    
    def __init__(self, course, key_path, key_content, username, repo_name):
        super().__init__()
        self.course = course
        self.key_path = key_path
        self.key_content = key_content
        self.username = username
        self.repo_name = repo_name
        self.abort_requested = False
    
    def run(self):
        """Run the publishing process in a background thread"""
        try:
            # 1. Set default commit message
            commit_message = tr(f"Update course: {self.course.title}")
            
            # 2. Check if directory is a git repository
            self.progress_update.emit(tr("Checking git repository..."))
            is_git_repo = CoursePublisher.is_git_repository(self.course.course_path)
            
            if not is_git_repo:
                # Initialize git repository
                self.progress_update.emit(tr("Initializing git repository..."))
                success = CoursePublisher.init_git_repository(self.course.course_path)
                if not success:
                    self.operation_complete.emit(False, tr("Failed to initialize git repository"), "")
                    return
            
            if self.abort_requested:
                self.operation_complete.emit(False, tr("Operation aborted"), "")
                return
                
            # 3. Commit changes
            self.progress_update.emit(tr("Committing changes..."))
            success = CoursePublisher.commit_changes(self.course.course_path, commit_message)
            if not success:
                logger.error(f"Failed to commit changes: {self.course.course_path}")
                # Continue anyway, as there might be no changes to commit
            
            if self.abort_requested:
                self.operation_complete.emit(False, tr("Operation aborted"), "")
                return
                
            # 4. Create remote repository if needed
            repo_url = None
            
            # Check if remote already exists
            self.progress_update.emit(tr("Checking for existing remote..."))
            existing_remote = CoursePublisher.get_remote_url(self.course.course_path)
            if existing_remote:
                repo_url = existing_remote
                self.progress_update.emit(tr("Using existing remote repository"))
            else:
                self.progress_update.emit(tr("Creating remote repository..."))
                success, new_repo_url, message = CoursePublisher.create_remote_repository(
                    self.key_content, self.repo_name, self.username
                )
                
                if not success:
                    self.operation_complete.emit(False, tr(f"Failed to create repository: {message}"), "")
                    return
                
                repo_url = new_repo_url
                
                if self.abort_requested:
                    self.operation_complete.emit(False, tr("Operation aborted"), "")
                    return
                    
                # Set up git remote
                self.progress_update.emit(tr("Setting up git remote..."))
                success = CoursePublisher.setup_git_remote(self.course.course_path, repo_url)
                if not success:
                    self.operation_complete.emit(False, tr("Failed to set up git remote"), "")
                    return
            
            if self.abort_requested:
                self.operation_complete.emit(False, tr("Operation aborted"), "")
                return
                
            # 5. Push to remote
            self.progress_update.emit(tr("Pushing to remote repository..."))
            success, error = CoursePublisher.push_to_remote(self.course.course_path)
            if not success:
                self.operation_complete.emit(False, tr(f"Failed to push to remote: {error}"), "")
                return
            
            # 6. Complete
            self.progress_update.emit(tr("Publish completed successfully!"))
            self.operation_complete.emit(True, tr(f"Course published successfully to {repo_url}"), repo_url)
            
        except Exception as e:
            logger.error(f"Error in publish worker: {str(e)}")
            self.operation_complete.emit(False, tr(f"Error during publishing: {str(e)}"), "")
    
    def abort(self):
        """Request abortion of the operation"""
        self.abort_requested = True
        self.progress_update.emit(tr("Aborting operation..."))

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

    def isComplete(self) -> bool:
        """Always return True to enable the Finish button"""
        return True
    
    def on_finished(self, result):
        """Handle wizard completion"""
        if result == QWizard.Accepted:
            # Get field values
            commit_message = self.field("commit_message")
            push_to_remote = self.field("push_to_remote")
            
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
                logger.error(f"Failed to commit changes: {self.course.course_path}")
            
            if push_to_remote:
                # Get SSH key content
                if not self.selected_key:
                    self.publish_completed.emit(False, tr("No SSH key selected"))
                    return
                
                # Check if remote already exists
                existing_remote = CoursePublisher.get_remote_url(self.course.course_path)
                
                # Set up git remote if needed
                if self.repo_url and (not existing_remote or self.repo_url != existing_remote):
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
