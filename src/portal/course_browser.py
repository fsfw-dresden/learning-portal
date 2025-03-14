import logging
from typing import Dict, List
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QScrollArea, QGridLayout, QProgressBar,
                            QStackedWidget,
                            QComboBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from core.models import Course, CourseCollection
from core.unit_scanner import UnitScanner
from portal.course_card import CourseCard
from portal.course_detail_view import CourseDetailView
from portal.abstract_unit_course_view import AbstractUnitCourseView

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

class UnitBrowserWidget(AbstractUnitCourseView):
    """Widget for browsing courses and their lessons"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scanner = UnitScanner()
        self.courses_by_title: Dict[str, Course] = {}
        self.all_courses: List[Course] = []
        self.collections: List[CourseCollection] = []
        self.initUI()
        self.load_courses()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Create stacked widget to switch between views
        self.stacked_widget = QStackedWidget()
        
        # Courses grid view
        self.courses_view = QWidget()
        courses_layout = QVBoxLayout(self.courses_view)
        
        # Header with title and collection filter
        header_layout = QHBoxLayout()
        
        # Title for courses view
        courses_title = QLabel(tr("Browse Courses"))
        courses_title.setFont(QFont("Arial", 20, QFont.Bold))
        header_layout.addWidget(courses_title)
        
        header_layout.addStretch()
        
        # Collection filter dropdown
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel(tr("Collection:")))
        
        self.collection_combo = QComboBox()
        self.collection_combo.setMinimumWidth(200)
        self.collection_combo.currentIndexChanged.connect(self.on_collection_changed)
        filter_layout.addWidget(self.collection_combo)
        
        header_layout.addLayout(filter_layout)
        courses_layout.addLayout(header_layout)
        
        # Scroll area for course cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(24)
        self.cards_layout.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(self.cards_container)
        
        courses_layout.addWidget(scroll)
        
        # Course detail view
        self.detail_view = CourseDetailView(writable=False)
        self.detail_view.back_clicked.connect(self.show_courses_view)
        self.detail_view.course_updated.connect(self.on_course_updated)
        
        # Add both views to stacked widget
        self.stacked_widget.addWidget(self.courses_view)
        self.stacked_widget.addWidget(self.detail_view)
        
        layout.addWidget(self.stacked_widget)
        
    def load_courses(self):
        """Load all courses and collections"""
        self.scanner = UnitScanner()
        self.all_courses = self.scanner.list_all_courses()
        self.collections = self.scanner.list_all_collections()
        
        # Populate collection dropdown
        self.populate_collection_dropdown()
        
        # Display all courses by default
        self.display_courses(self.all_courses)
        
    def populate_collection_dropdown(self):
        """Populate the collection dropdown with available collections"""
        self.collection_combo.clear()
        
        # Add "All Collections" option
        self.collection_combo.addItem(tr("All Collections"), None)
        
        # Add each collection
        for collection in self.collections:
            self.collection_combo.addItem(collection.title, collection.unique_collection_name)
            
    def on_collection_changed(self, index):
        """Handle collection filter change"""
        if index == 0:  # "All Collections"
            # Display all courses
            self.display_courses(self.all_courses)
        else:
            # Get selected collection name
            collection_name = self.collection_combo.itemData(index)
            
            # Filter courses by collection
            filtered_courses = self.scanner.filter_course_by_collection(collection_name)
            
            # Display filtered courses
            self.display_courses(filtered_courses)
        
    def display_courses(self, courses: List[Course]):
        """Display course cards in a grid"""
        # Sort courses alphabetically by title
        courses.sort(key=lambda course: course.title.lower())
        
        # Store courses by title for quick lookup
        self.courses_by_title = {course.title: course for course in courses}
        
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Add new cards
        for i, course in enumerate(courses):
            row = i // 3  # 3 cards per row
            col = i % 3
            
            card = CourseCard(course)
            card.clicked.connect(self.show_course_detail)
            
            self.cards_layout.addWidget(card, row, col)
            
        # Show "No courses found" message if no courses are available
        if not courses:
            no_courses_label = QLabel(tr("No courses found in this collection"))
            no_courses_label.setAlignment(Qt.AlignCenter)
            no_courses_label.setStyleSheet("color: #888; font-size: 16px; padding: 40px;")
            self.cards_layout.addWidget(no_courses_label, 0, 0, 1, 3)
    
    def on_course_updated(self, course: Course):
        """Handle when a course is updated"""
        # Update the course in our local cache
        if course.title in self.courses_by_title:
            self.courses_by_title[course.title] = course
            
        # Reload the courses to reflect changes
        self.load_courses()
    
    def show_course_detail(self, course_title: str):
        """Show detailed view for a specific course"""
        if course_title in self.courses_by_title:
            course = self.courses_by_title[course_title]
            
            # Check if the course is in a writable collection
            writable = False
            for collection in self.collections:
                if collection.unique_collection_name == course.collection_name and collection.writable:
                    writable = True
                    break
                    
            logger.info(f"Course {course_title} is in writable collection: {writable}")
            # Set writable flag on detail view
            self.detail_view.set_writable(writable)
            
            # Set the course
            self.detail_view.set_course(course)
            self.stacked_widget.setCurrentWidget(self.detail_view)
    
    def show_courses_view(self):
        """Show the main courses grid view"""
        self.stacked_widget.setCurrentWidget(self.courses_view)
        
    def reload(self):
        """Implement the abstract reload method"""
        # Store the current collection selection
        current_index = self.collection_combo.currentIndex()
        
        # Reload courses and collections
        self.load_courses()
        
        # Restore the previous collection selection if possible
        if current_index < self.collection_combo.count():
            self.collection_combo.setCurrentIndex(current_index)
        else:
            self.collection_combo.setCurrentIndex(0)  # Default to "All Collections" 