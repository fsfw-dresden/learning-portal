from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                            QComboBox, QPushButton, QFormLayout)
from PyQt5.QtCore import Qt
from core.unit_scanner import UnitScanner
from portal.tr import tr

class UnitCreateForm(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scanner = UnitScanner()
        self.setWindowTitle(tr("Create New Unit"))
        self.setModal(True)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # Course name combobox with autocomplete
        self.course_input = QComboBox()
        self.course_input.setEditable(True)
        self.course_input.setInsertPolicy(QComboBox.InsertPolicy.InsertAlphabetically)
        # Get existing course names
        existing_courses = set(course.name for course in self.scanner.courses)
        self.course_input.addItems(sorted(existing_courses))
        form_layout.addRow(tr("Course Name:"), self.course_input)
        
        # Lesson name input
        self.lesson_input = QLineEdit()
        form_layout.addRow(tr("Lesson Name:"), self.lesson_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QVBoxLayout()
        create_button = QPushButton(tr("Create"))
        create_button.clicked.connect(self.accept)
        cancel_button = QPushButton(tr("Cancel"))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
