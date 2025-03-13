from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QFrame, QSizePolicy, QHBoxLayout, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QColor, QPalette
from core.models import Course
from pathlib import Path

class CourseCard(QFrame):
    """
    A card widget that displays a course with its title, description,
    and preview image if available. Designed to be used in the course browser.
    """
    clicked = pyqtSignal(str)
    
    def __init__(self, course: Course, parent=None):
        super().__init__(parent)
        self.course = course
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        
        # Set fixed size for consistent grid layout
        self.setMinimumSize(300, 200)
        self.setMaximumSize(400, 250)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
        # Get current palette colors for theme-aware styling
        app = QApplication.instance()
        palette = app.palette()
        base_color = palette.color(QPalette.Base)
        text_color = palette.color(QPalette.Text)
        highlight_color = palette.color(QPalette.Highlight)
        
        # Calculate slightly different colors for hover effects
        hover_bg = base_color.lighter(110) if base_color.lightness() < 128 else base_color.darker(105)
        border_color = palette.color(QPalette.Mid)
        hover_border = highlight_color.lighter(130) if highlight_color.lightness() < 128 else highlight_color
        
        # Style the card with theme-aware colors
        self.setStyleSheet(f"""
            CourseCard {{
                background-color: {base_color.name()};
                border-radius: 8px;
                border: 1px solid {border_color.name()};
            }}
            CourseCard:hover {{
                border: 1px solid {hover_border.name()};
                background-color: {hover_bg.name()};
            }}
        """)
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        # Get current palette for theme-aware text colors
        palette = QApplication.instance().palette()
        text_color = palette.color(QPalette.Text)
        disabled_color = palette.color(QPalette.Disabled, QPalette.Text)
        
        # Course image
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(100)
        self.image_label.setMaximumHeight(150)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setScaledContents(False)
        
        # Use theme-aware background for image placeholder
        placeholder_color = palette.color(QPalette.AlternateBase).name()
        self.image_label.setStyleSheet(f"background-color: {placeholder_color}; border-radius: 4px;")
        
        # Set image if available
        if hasattr(self.course, 'preview_path') and self.course.preview_path:
            pixmap = QPixmap(str(self.course.preview_path))
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.width(), 
                    self.image_label.height(),
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))
        
        layout.addWidget(self.image_label)
        
        # Course title - use system default font instead of palette.font()
        self.title_label = QLabel(self.course.title)
        font = QApplication.font()  # Get application default font
        title_font = QFont(font.family(), 12, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # Use system text color
        self.title_label.setStyleSheet(f"color: {text_color.name()};")
        layout.addWidget(self.title_label)
        
        # Course description (if available)
        if hasattr(self.course, 'description') and self.course.description:
            description = self.course.description
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:97] + "..."
                
            self.description_label = QLabel(description)
            self.description_label.setWordWrap(True)
            # Use slightly muted text color based on system palette
            self.description_label.setStyleSheet(f"color: {disabled_color.name()};")
            self.description_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            layout.addWidget(self.description_label)
        
        # Lesson count
        lesson_count = len(self.course.lessons) if hasattr(self.course, 'lessons') else 0
        lesson_text = f"{lesson_count} lesson{'s' if lesson_count != 1 else ''}"
        
        self.lesson_count_label = QLabel(lesson_text)
        # Use disabled text color for secondary information
        self.lesson_count_label.setStyleSheet(f"color: {disabled_color.name()}; font-size: 11px;")
        self.lesson_count_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        layout.addWidget(self.lesson_count_label)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
    def mousePressEvent(self, event):
        """Handle mouse press events to make the card clickable"""
        super().mousePressEvent(event)
        self.clicked.emit(self.course.title)
        
    def enterEvent(self, event):
        """Handle mouse enter events for hover effect"""
        super().enterEvent(event)
        self.setCursor(Qt.PointingHandCursor)
        
    def leaveEvent(self, event):
        """Handle mouse leave events for hover effect"""
        super().leaveEvent(event)
        self.setCursor(Qt.ArrowCursor) 