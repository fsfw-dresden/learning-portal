"""
Demo application for the dataclass forms module.
"""

import sys
import logging
from dataclasses import dataclass, field
from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
)

from dataclass_forms.form_generator import DataclassFormGenerator, FormField


@dataclass
class Author:
    name: str
    email: Optional[str] = None
    bio: str = ""


@dataclass
class Course:
    title: str
    skill_level: int = field(
        default=0,
        metadata=FormField.number(min_value=0, max_value=10)
    )  # 0-10 skill level with enforced range
    authors: List[str] = field(default_factory=list)
    description: str = field(
        default="",
        metadata=FormField.text(multiline=True)
    )
    is_published: bool = False
    
    # Nested dataclass example
    main_author: Optional[Author] = None


class DemoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dataclass Forms Demo")
        self.resize(600, 800)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Add title
        title = QLabel("Dataclass Forms Demo")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Create a sample course
        sample_course = Course(
            title="Introduction to Python",
            skill_level=5,
            authors=["John Doe", "Jane Smith"],
            description="Learn the basics of Python programming.",
            is_published=True,
            main_author=Author(
                name="John Doe",
                email="john@example.com",
                bio="Experienced Python developer and educator."
            )
        )
        
        # Create the form
        self.form = DataclassFormGenerator.create_form(Course)
        self.form.set_value(sample_course)
        layout.addWidget(self.form)
        
        # Add buttons
        buttons_layout = QHBoxLayout()
        
        reset_button = QPushButton("Reset to Default")
        reset_button.clicked.connect(lambda: self.form.set_value(sample_course))
        
        get_value_button = QPushButton("Get Value")
        get_value_button.clicked.connect(self.show_current_value)
        
        buttons_layout.addWidget(reset_button)
        buttons_layout.addWidget(get_value_button)
        layout.addLayout(buttons_layout)
        
        # Add a label to show the current value
        self.value_label = QLabel()
        self.value_label.setWordWrap(True)
        self.value_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        layout.addWidget(self.value_label)
        
        # Show initial value
        self.show_current_value()
    
    def show_current_value(self):
        """Show the current value of the form."""
        course = self.form.get_value()
        if course:
            value_text = f"Title: {course.title}\n"
            value_text += f"Skill Level: {course.skill_level}\n"
            value_text += f"Authors: {', '.join(course.authors)}\n"
            value_text += f"Description: {course.description}\n"
            value_text += f"Published: {course.is_published}\n"
            
            if course.main_author:
                value_text += f"\nMain Author:\n"
                value_text += f"  Name: {course.main_author.name}\n"
                value_text += f"  Email: {course.main_author.email}\n"
                value_text += f"  Bio: {course.main_author.bio}\n"
            
            self.value_label.setText(value_text)


def main():
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('dataclass_forms')
    logger.setLevel(logging.DEBUG)
    
    # Create and show the application
    app = QApplication(sys.argv)
    window = DemoApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
