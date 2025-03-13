import random
from typing import List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QGridLayout, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QProgressBar,
                            QFrame, QPushButton, QStackedWidget,
                            QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont
from core.models import BaseLesson, LessonMetadata, Course
from portal.simple_unit_card import SimpleUnitCard
from portal.unit_card import UnitCard

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

class CourseDetailView(QWidget):
    """Detailed view of a course and its lessons"""
    back_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Header with back button
        header_layout = QHBoxLayout()
        self.back_button = QPushButton("← Back to Courses")
        self.back_button.clicked.connect(self.back_clicked.emit)
        header_layout.addWidget(self.back_button)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Course information section
        info_layout = QHBoxLayout()
        
        # Left side - course image (if available)
        self.image_label = QLabel()
        self.image_label.setMinimumSize(200, 150)
        self.image_label.setMaximumSize(300, 225)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setStyleSheet("background-color: #f0f0f0; border-radius: 8px;")
        info_layout.addWidget(self.image_label)
        
        # Right side - course title and description
        course_info = QVBoxLayout()
        self.title_label = QLabel()
        self.title_label.setFont(QFont("Arial", 18, QFont.Bold))
        course_info.addWidget(self.title_label)
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #555;")
        course_info.addWidget(self.description_label)
        
        # Collection name
        self.collection_label = QLabel()
        self.collection_label.setStyleSheet("color: #777; font-style: italic;")
        course_info.addWidget(self.collection_label)
        
        course_info.addStretch()
        
        info_layout.addLayout(course_info)
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
        
    def toggle_lesson_view(self, checked):
        """Toggle between table and card view for lessons"""
        if checked:  # Table view selected
            self.lessons_stack.setCurrentIndex(0)
        else:  # Card view selected
            self.lessons_stack.setCurrentIndex(1)
        
    def set_course(self, course: Course):
        """Update the view with course information"""
        self.title_label.setText(course.title)
        
        # Set description if available
        description = getattr(course, 'description', '')
        self.description_label.setText(description or tr("No description available"))
        
        # Set collection name
        self.collection_label.setText(f"Collection: {course.collection_name}")
        
        # Set image if available
        if hasattr(course, 'preview_path') and course.preview_path:
            pixmap = QPixmap(str(course.preview_path))
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap)
        else:
            # Use placeholder
            placeholder = QPixmap(300, 225)
            placeholder.fill(Qt.lightGray)
            self.image_label.setPixmap(placeholder)
        
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
            row = i // 2  # 2 cards per row
            col = i % 2
            
            card = UnitCard(lesson) if isinstance(lesson, LessonMetadata) else SimpleUnitCard(lesson)
            self.lessons_card_layout.addWidget(card, row, col) 