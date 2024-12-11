import os
import subprocess
from pathlib import Path
from venv import logger
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                            QComboBox, QPushButton, QFormLayout, QMessageBox)
from PyQt5.QtCore import Qt
from core.unit_scanner import UnitScanner
from core.config import PortalConfig
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
        # Get existing course titles
        existing_courses = set(course.title for course in self.scanner.courses)
        self.course_input.addItems(sorted(existing_courses))
        form_layout.addRow(tr("Course Name:"), self.course_input)
        
        # Lesson name input
        self.lesson_input = QLineEdit()
        form_layout.addRow(tr("Lesson Name:"), self.lesson_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QVBoxLayout()
        create_button = QPushButton(tr("Create"))
        create_button.clicked.connect(self.create_unit)
        cancel_button = QPushButton(tr("Cancel"))
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(create_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
    def create_unit(self):
        course_name = self.course_input.currentText().strip()
        lesson_name = self.lesson_input.text().strip()
        
        if not course_name or not lesson_name:
            QMessageBox.warning(self, tr("Error"), tr("Both course and lesson name are required."))
            return
            
        # Create sanitized directory names
        course_dir = self._sanitize_name(course_name)
        lesson_dir = self._sanitize_name(lesson_name)
        
        # Get the base path for units
        config = PortalConfig.load()
        base_path = config.get_scan_path()
        if isinstance(base_path, list):
            base_path = base_path[0]  # Use first path if multiple
        
        course_collection_path = base_path / "drafts"
        course_path = course_collection_path / course_dir
        lesson_path = course_path / lesson_dir
        markdown_file = lesson_path / "README.md"

        logger.info(f"Creating lesson at {lesson_path}")
        
        # Check if lesson already exists
        if lesson_path.exists():
            response = QMessageBox.question(
                self,
                tr("Lesson exists"),
                tr("This lesson already exists. Would you like to edit it?"),
                QMessageBox.Yes | QMessageBox.No
            )
            if response == QMessageBox.Yes:
                self._open_in_editor(markdown_file)
                self.accept()
            return
            
        # Create directories
        lesson_path.mkdir(parents=True, exist_ok=True)
        
        # Create template markdown file
        template = f"""<!--
author:  {os.getenv('USER', 'Anonymous')}
email:   
version:  0.0.1
language: en
narrator: US English Female

comment:  A new lesson for {course_name}

link:     https://cdn.jsdelivr.net/chartist.js/latest/chartist.min.css

script:   https://cdn.jsdelivr.net/chartist.js/latest/chartist.min.js

-->

# {lesson_name}

## Introduction

Welcome to this new lesson!

"""
        
        with open(markdown_file, 'w') as f:
            f.write(template)
            
        # Open in editor
        self._open_in_editor(markdown_file)
        self.accept()
        
    def _sanitize_name(self, name: str) -> str:
        """Convert a display name to a safe directory name"""
        # Replace spaces with dashes and remove special characters
        return "".join(c.lower() if c.isalnum() or c in '-_ ' else '-' 
                      for c in name).strip().replace(' ', '-')
        
    def _open_in_editor(self, markdown_file: Path):
        """Open the markdown file in the configured editor"""
        config = PortalConfig.load()
        url = f"{config.liascript_editor_url}{config.liascript_editor_proxy_static_url}{markdown_file.relative_to(config.get_scan_path())}"
        command = f"{config.liascript_editor_open_command}{url}"
        subprocess.Popen(command, shell=True)
