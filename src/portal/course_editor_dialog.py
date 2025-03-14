"""
Dialog for editing course details using dataclass forms.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QScrollArea, QMessageBox, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal

from core.models import Course, CourseMetadata
from src.dataclass_forms.form_generator import DataclassFormGenerator

def tr(text: str) -> str:
    """Helper function for translations"""
    from PyQt5.QtWidgets import QApplication
    return QApplication.translate("Portal", text)

class CourseEditorDialog(QDialog):
    """Dialog for editing course details"""
    
    course_updated = pyqtSignal(Course)
    
    def __init__(self, course: Course, parent=None):
        super().__init__(parent)
        self.course = course
        self.setWindowTitle(tr("Edit Course"))
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(tr("Edit Course Details"))
        title_label.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title_label)
        
        # Create a form for the course metadata
        self.metadata_form = DataclassFormGenerator.create_form(CourseMetadata, self)
        self.metadata_form.set_value(self.course.metadata)
        
        # Add the form to a scroll area
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.metadata_form)
        layout.addWidget(scroll)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton(tr("Save"))
        self.cancel_button = QPushButton(tr("Cancel"))
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.cancel_button)
        layout.addLayout(buttons_layout)
        
        # Connect buttons
        self.save_button.clicked.connect(self.save_course)
        self.cancel_button.clicked.connect(self.reject)
        
    def save_course(self):
        """Save the course with updated metadata"""
        try:
            # Get the updated metadata from the form
            updated_metadata = self.metadata_form.get_value()
            
            # Update the course metadata
            self.course.metadata = updated_metadata
            
            # Update the course title to match metadata
            self.course.title = updated_metadata.title
            self.course.collection_name = updated_metadata.collection_name
            
            # Save the course
            if self.course.save():
                # Emit signal that course was updated
                self.course_updated.emit(self.course)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    tr("Error"),
                    tr("Failed to save course metadata.")
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                tr("Error"),
                tr(f"An error occurred: {str(e)}")
            )
