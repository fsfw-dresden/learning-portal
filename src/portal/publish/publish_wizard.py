"""
Wizard for publishing courses to git repositories.
"""

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QLabel, QLineEdit, 
    QCheckBox, QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from pathlib import Path
import logging

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
        
        # Update status when page is shown
        self.initializePage()
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        if self.course.course_path:
            is_git, status_msg = CoursePublisher.get_git_status(self.course.course_path)
            self.status_label.setText(tr(f"Git Status: {status_msg}"))
        else:
            self.status_label.setText(tr("Course path not set"))

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
        layout.addWidget(self.summary_label)
    
    def initializePage(self):
        """Initialize the page when it's shown"""
        commit_message = self.field("commit_message")
        push_to_remote = self.field("push_to_remote")
        
        summary = tr(f"Course: {self.course.title}\n")
        summary += tr(f"Commit Message: {commit_message}\n")
        summary += tr(f"Push to Remote: {'Yes' if push_to_remote else 'No'}")
        
        self.summary_label.setText(summary)

class PublishWizard(QWizard):
    """Wizard for publishing courses to git repositories"""
    
    publish_completed = pyqtSignal(bool, str)  # Success, message
    
    def __init__(self, course: Course, parent=None):
        super().__init__(parent)
        self.course = course
        
        self.setWindowTitle(tr("Publish Course"))
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add pages
        self.addPage(PublishIntroPage(course))
        self.addPage(PublishOptionsPage(course))
        self.addPage(PublishSummaryPage(course))
        
        # Connect signals
        self.finished.connect(self.on_finished)
    
    def on_finished(self, result):
        """Handle wizard completion"""
        if result == QWizard.Accepted:
            # This is where we would actually publish the course
            # For now, just emit a success signal
            self.publish_completed.emit(True, tr("Course published successfully (dummy implementation)"))
            
            # In a real implementation, we would:
            # 1. Check if the directory is a git repository
            # 2. If not, initialize one
            # 3. Add all files
            # 4. Commit with the provided message
            # 5. Push to remote if requested
