import random
import os
import shutil
from typing import List, Optional
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QGridLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QProgressBar,
                            QFrame, QPushButton, QStackedWidget,
                            QButtonGroup, QRadioButton, QInputDialog,
                            QToolButton, QFileDialog, QMessageBox)
from portal.course_editor_dialog import CourseEditorDialog
from portal.publish.course_publisher import CoursePublisher
from portal.publish.publish_wizard import PublishWizard
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QPixmap, QFont, QIcon
from core.models import BaseLesson, LessonMetadata, Lesson, Course
from portal.unit_card import UnitCard
import logging

logger = logging.getLogger(__name__)

def tr(text: str) -> str:
    """Helper function for translations"""
    from PyQt5.QtWidgets import QApplication
    return QApplication.translate("Portal", text)

class LessonProgressWidget(QWidget):
    """Widget to display lesson progress information"""
    def __init__(self, progress_value: int, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(progress_value)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setMinimumWidth(100)
        self.progress_bar.setMaximumWidth(150)
        
        layout.addWidget(self.progress_bar)

class ImageWithEditButton(QWidget):
    """Image widget with an edit button overlay"""
    edit_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        # Use a layout to position the image and button
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Container for image and edit button
        self.container = QFrame()
        self.container.setMinimumSize(200, 150)
        self.container.setMaximumSize(300, 225)
        self.container.setStyleSheet("border-radius: 8px;")
        
        # Use absolute positioning for the container
        container_layout = QVBoxLayout(self.container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setAlignment(Qt.AlignCenter)  # Center the image
        
        # Image label
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        # Use Qt.KeepAspectRatio instead of setScaledContents(True)
        self.image_label.setScaledContents(False)
        container_layout.addWidget(self.image_label)
        
        # Edit button (positioned in the top-right corner)
        self.edit_button = QToolButton(self.container)
        self.edit_button.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_button.setToolTip(tr("Change image"))
        self.edit_button.clicked.connect(self.edit_clicked.emit)
        self.edit_button.setStyleSheet("""
            QToolButton {
                background-color: rgba(40, 40, 40, 0.9);
                border-radius: 12px;
                padding: 4px;
                color: white;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 1.0);
                border: 1px solid white;
            }
        """)
        self.edit_button.setIconSize(QSize(16, 16))
        self.edit_button.setFixedSize(QSize(24, 24))
        self.edit_button.move(self.container.width() - 30, 6)  # Position in top-right
        self.edit_button.setVisible(False)  # Hidden by default
        
        layout.addWidget(self.container)
        
    def setPixmap(self, pixmap: QPixmap):
        """Set the image pixmap"""
        # Get the container size to ensure we don't exceed it
        container_width = self.container.width()
        container_height = self.container.height()
        
        # If the widget hasn't been properly sized yet, use minimum size
        if container_width <= 1 or container_height <= 1:
            container_width = self.container.minimumWidth()
            container_height = self.container.minimumHeight()
        
        # Scale the pixmap to fit within the container while preserving aspect ratio
        # Use a slightly smaller target size to prevent edge cropping
        target_width = int(container_width * 0.9)
        target_height = int(container_height * 0.9)
        
        logger.info(f"Setting pixmap: {pixmap.size()} to container size: {container_width}x{container_height}")
        
        scaled_pixmap = pixmap.scaled(
            target_width, 
            target_height,
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        
        self.image_label.setPixmap(scaled_pixmap)
        
    def setEditVisible(self, visible: bool):
        """Show or hide the edit button"""
        self.edit_button.setVisible(visible)
        
    def resizeEvent(self, event):
        """Handle resize events to reposition the edit button"""
        super().resizeEvent(event)
        # Reposition the edit button when the widget is resized
        self.edit_button.move(self.container.width() - 30, 6)

class CourseDetailView(QWidget):
    """Detailed view of a course and its lessons"""
    back_clicked = pyqtSignal()
    course_updated = pyqtSignal(Course)
    
    def __init__(self, writable=False, parent=None):
        super().__init__(parent)
        self.writable = writable
        self.course = None
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Header with back button and publish status
        header_layout = QHBoxLayout()
        self.back_button = QPushButton("← Back to Courses")
        self.back_button.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        
        # Publish status button (only visible if writable)
        self.publish_status_button = QPushButton()
        self.publish_status_button.setFixedSize(120, 30)
        self.publish_status_button.clicked.connect(self.open_publish_wizard)
        self.publish_status_button.setVisible(self.writable)
        header_layout.addWidget(self.publish_status_button)
        
        layout.addLayout(header_layout)
        
        # Course information section
        info_layout = QHBoxLayout()
        
        # Right side - course title and description
        course_info = QVBoxLayout()
        
        # Title with optional edit button
        title_layout = QHBoxLayout()
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        title_layout.addWidget(self.title_label)
        
        # Edit button (only visible if writable)
        self.edit_title_button = QToolButton()
        self.edit_title_button.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_title_button.setToolTip(tr("Edit course title"))
        self.edit_title_button.clicked.connect(self.edit_course_title)
        self.edit_title_button.setVisible(self.writable)
        title_layout.addWidget(self.edit_title_button)
        
        title_layout.addStretch()
        course_info.addLayout(title_layout)
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555;")
        course_info.addWidget(self.description_label)
        
        # Collection name
        self.collection_label = QLabel()
        self.collection_label.setStyleSheet("color: #777; font-style: italic;")
        course_info.addWidget(self.collection_label)
        
        course_info.addStretch()
        
        # Left side - course info
        info_layout.addLayout(course_info, 3)
        
        # Right side - course image with edit button
        self.image_widget = ImageWithEditButton()
        self.image_widget.edit_clicked.connect(self.edit_course_image)
        info_layout.addWidget(self.image_widget, 1)
        
        layout.addLayout(info_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # View toggle for lessons (Table or Cards)
        toggle_layout = QHBoxLayout()
        toggle_layout.addWidget(QLabel(tr("Lessons:")))
        toggle_layout.addStretch()
        
        self.view_toggle_group = QButtonGroup(self)
        self.table_view_button = QRadioButton(tr("Table View"))
        self.table_view_button.setChecked(True)
        self.card_view_button = QRadioButton(tr("Card View"))
        
        self.view_toggle_group.addButton(self.table_view_button)
        self.view_toggle_group.addButton(self.card_view_button)
        
        toggle_layout.addWidget(self.table_view_button)
        toggle_layout.addWidget(self.card_view_button)
        
        layout.addLayout(toggle_layout)
        
        # Stacked widget for different lesson views
        self.lessons_stack = QStackedWidget()
        
        # Table view for lessons
        self.lessons_table = QTableWidget()
        self.lessons_table.setColumnCount(4)
        self.lessons_table.setHorizontalHeaderLabels(["Lesson", "Status", "Progress", "Duration"])
        self.lessons_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.lessons_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.lessons_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.lessons_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.lessons_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.lessons_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.lessons_table.verticalHeader().setVisible(False)
        
        # Card view for lessons
        self.lessons_card_view = QScrollArea()
        self.lessons_card_view.setWidgetResizable(True)
        self.lessons_card_container = QWidget()
        self.lessons_card_layout = QGridLayout(self.lessons_card_container)
        self.lessons_card_layout.setSpacing(16)
        self.lessons_card_view.setWidget(self.lessons_card_container)
        
        # Add both views to stack
        self.lessons_stack.addWidget(self.lessons_table)
        self.lessons_stack.addWidget(self.lessons_card_view)
        
        # Connect toggle buttons
        self.table_view_button.toggled.connect(self.toggle_lesson_view)
        
        layout.addWidget(self.lessons_stack)
    
    def set_writable(self, writable: bool):
        """Set whether the course details can be edited"""
        self.writable = writable
        self.edit_title_button.setVisible(writable)
        self.image_widget.setEditVisible(writable)
        self.publish_status_button.setVisible(writable)
        
        # Update publish status if writable
        if writable and self.course and self.course.course_path:
            self.update_publish_status()
    
    def edit_course_title(self):
        """Open a dialog to edit the course details"""
        if not self.course:
            return
            
        # Create and show the course editor dialog
        editor_dialog = CourseEditorDialog(self.course, self)
        editor_dialog.course_updated.connect(self.on_course_updated)
        editor_dialog.exec_()
    
    def on_course_updated(self, course):
        """Handle course updated signal from editor dialog"""
        # Update the UI with the new course details
        self.title_label.setText(course.title)
        self.description_label.setText(course.description or tr("No description available"))
        self.collection_label.setText(f"Collection: {course.collection_name}")
        
        # Emit signal that course was updated
        self.course_updated.emit(course)
    
    def edit_course_image(self):
        """Open a file dialog to select a new course image"""
        if not self.course or not self.course.course_path:
            return
            
        # Open file dialog to select an image
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Select Course Image"),
            "",
            tr("Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        )
        
        if not file_path:
            return  # User canceled
            
        try:
            # Determine target filename (preserve extension)
            _, ext = os.path.splitext(file_path)
            target_filename = f"preview{ext}"
            target_path = self.course.course_path / target_filename
            
            # Copy the image file to the course directory
            shutil.copy2(file_path, target_path)
            
            # Update course metadata
            self.course.preview_image = target_filename
            
            # Update the displayed image
            pixmap = QPixmap(str(target_path))
            if not pixmap.isNull():
                self.image_widget.setPixmap(pixmap)
            
            # Save the changes
            if self.course.save():
                # Emit signal that course was updated
                self.course_updated.emit(self.course)
                
            logger.info(f"Updated course image: {target_path}")
            
        except Exception as e:
            logger.error(f"Error updating course image: {e}")
            QMessageBox.warning(
                self,
                tr("Error"),
                tr(f"Failed to update course image: {str(e)}")
            )
        
    def toggle_lesson_view(self, checked):
        """Toggle between table and card view for lessons"""
        if checked:  # Table view selected
            self.lessons_stack.setCurrentIndex(0)
        else:  # Card view selected
            self.lessons_stack.setCurrentIndex(1)
        
    def update_publish_status(self):
        """Update the publish status button based on git status"""
        if not self.course or not self.course.course_path:
            self.publish_status_button.setText(tr("Not Published"))
            self.publish_status_button.setStyleSheet("background-color: #ff6b6b; color: white;")
            return
            
        is_git_repo = CoursePublisher.is_git_repository(self.course.course_path)
        
        if not is_git_repo:
            self.publish_status_button.setText(tr("Not Published"))
            self.publish_status_button.setStyleSheet("background-color: #ff6b6b; color: white;")
            return
            
        is_clean, status_msg = CoursePublisher.get_git_status(self.course.course_path)
        
        if is_clean and "up to date" in status_msg:
            self.publish_status_button.setText(tr("Published"))
            self.publish_status_button.setStyleSheet("background-color: #51cf66; color: white;")
        elif is_clean and "no commits" in status_msg:
            self.publish_status_button.setText(tr("Not Published"))
            self.publish_status_button.setStyleSheet("background-color: #ff6b6b; color: white;")
        else:
            self.publish_status_button.setText(tr("Needs Update"))
            self.publish_status_button.setStyleSheet("background-color: #fcc419; color: white;")
    
    def open_publish_wizard(self):
        """Open the publish wizard for the current course"""
        if not self.course or not self.course.course_path:
            QMessageBox.warning(
                self,
                tr("Cannot Publish"),
                tr("Course path is not set.")
            )
            return
            
        wizard = PublishWizard(self.course, self)
        wizard.publish_completed.connect(self.on_publish_completed)
        wizard.exec_()
    
    def on_publish_completed(self, success, message):
        """Handle publish completion"""
        if success:
            QMessageBox.information(
                self,
                tr("Publish Successful"),
                message
            )
            # Update status after publishing
            self.update_publish_status()
        else:
            QMessageBox.warning(
                self,
                tr("Publish Failed"),
                message
            )
    
    def set_course(self, course: Course):
        """Update the view with course information"""
        self.course = course
        self.title_label.setText(course.title)
        
        # Set description if available
        description = course.description
        self.description_label.setText(description or tr("No description available"))
        
        # Set collection name
        self.collection_label.setText(f"Collection: {course.collection_name}")
        
        # Update publish status if writable
        if self.writable and course.course_path:
            self.update_publish_status()
        
        # Set image if available
        if course.preview_path:
            pixmap = QPixmap(str(course.preview_path))
            if not pixmap.isNull():
                self.image_widget.setPixmap(pixmap)
        else:
            # Use placeholder
            placeholder = QPixmap(300, 225)
            placeholder.fill(Qt.lightGray)
            self.image_widget.setPixmap(placeholder)
        
        # Populate lessons in both views
        self.populate_lessons_table(course.lessons)
        self.populate_lessons_cards(course.lessons)
        
    def populate_lessons_table(self, lessons: List[BaseLesson]):
        """Populate the lessons table with lessons from the course"""
        self.lessons_table.setRowCount(len(lessons))
        
        for i, lesson in enumerate(lessons):
            # Lesson title
            title_item = QTableWidgetItem(lesson.title)
            self.lessons_table.setItem(i, 0, title_item)
            
            # Status (completed, in progress, not started)
            status_options = ["Not Started", "In Progress", "Completed"]
            status = random.choice(status_options)
            status_item = QTableWidgetItem(status)
            self.lessons_table.setItem(i, 1, status_item)
            
            # Progress bar
            progress_value = 0
            if status == "Completed":
                progress_value = 100
            elif status == "In Progress":
                progress_value = random.randint(10, 90)
            
            progress_widget = LessonProgressWidget(progress_value)
            self.lessons_table.setCellWidget(i, 2, progress_widget)
            
            # Duration (placeholder)
            duration = f"{random.randint(5, 30)} min"
            duration_item = QTableWidgetItem(duration)
            self.lessons_table.setItem(i, 3, duration_item)
    
    def populate_lessons_cards(self, lessons: List[BaseLesson]):
        """Populate the card view with lesson cards"""
        # Clear existing cards
        while self.lessons_card_layout.count():
            item = self.lessons_card_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # Add lesson cards
        for i, lesson in enumerate(lessons):
            row = i // 3
            col = i % 3
            
            card = UnitCard(lesson)
            self.lessons_card_layout.addWidget(card, row, col) 
