from PyQt5.QtWidgets import (QVBoxLayout, QLabel, 
                            QHBoxLayout, QFrame, QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QFont, QPalette
from core.models import BaseLesson, Lesson
from portal.horizontal_star_rating import HorizontalStarRating

class UnitCard(QFrame):
    """
    A card widget that displays a lesson with its title, subjects,
    and preview image if available.
    """
    clicked = pyqtSignal(object)
    
    def __init__(self, lesson: BaseLesson, parent=None):
        super().__init__(parent)
        self.lesson = lesson
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setLineWidth(1)
        self.setMidLineWidth(0)
        
        # Set fixed size for consistent grid layout
        self.setMinimumSize(200, 150)
        self.setMaximumSize(300, 200)
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
            UnitCard {{
                background-color: {base_color.name()};
                border-radius: 8px;
                border: 1px solid {border_color.name()};
            }}
            UnitCard:hover {{
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
        
        # Check if lesson has metadata
        has_metadata = isinstance(self.lesson, Lesson) and self.lesson.metadata is not None
        
        # Lesson image (if available)
        self.image_label = QLabel()
        self.image_label.setMinimumHeight(80)
        self.image_label.setMaximumHeight(100)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        # Use theme-aware background for image placeholder
        placeholder_color = palette.color(QPalette.AlternateBase).name()
        self.image_label.setStyleSheet(f"background-color: {placeholder_color}; border-radius: 4px;")
        
        # Set image if available
        if self.lesson.preview_path:
            pixmap = QPixmap(str(self.lesson.preview_path))
            if not pixmap.isNull():
                self.image_label.setPixmap(pixmap.scaled(
                    self.image_label.width(), 
                    self.image_label.height(),
                    Qt.KeepAspectRatio, 
                    Qt.SmoothTransformation
                ))
        
        layout.addWidget(self.image_label)
        
        # Lesson title - use system default font
        self.title_label = QLabel(self.lesson.title)
        font = QApplication.font()  # Get application default font
        title_font = QFont(font.family(), 10, QFont.Bold)
        self.title_label.setFont(title_font)
        self.title_label.setWordWrap(True)
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        # Use system text color
        self.title_label.setStyleSheet(f"color: {text_color.name()};")
        layout.addWidget(self.title_label)
        
        # Subject tags (if available)
        if has_metadata and self.lesson.metadata.subjects:
            subjects_layout = QHBoxLayout()
            subjects_layout.setSpacing(4)
            
            # Get theme-aware colors for subject tags
            highlight_color = palette.color(QPalette.Highlight)
            
            # Create a lighter/darker version of the highlight color for the background
            tag_bg = highlight_color.lighter(160) if highlight_color.lightness() < 128 else highlight_color.darker(160)
            tag_text = highlight_color.darker(50) if highlight_color.lightness() > 128 else highlight_color.lighter(200)
            
            for subject in self.lesson.metadata.subjects[:2]:  # Show max 2 subjects
                subject_label = QLabel(subject)
                subject_label.setStyleSheet(f"""
                    background-color: {tag_bg.name()};
                    color: {tag_text.name()};
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 10px;
                """)
                subjects_layout.addWidget(subject_label)
                
            if len(self.lesson.metadata.subjects) > 2:
                more_label = QLabel(f"+{len(self.lesson.metadata.subjects) - 2}")
                more_label.setStyleSheet(f"""
                    color: {disabled_color.name()};
                    font-size: 10px;
                    padding: 2px 0px;
                """)
                subjects_layout.addWidget(more_label)
                
            subjects_layout.addStretch()
            layout.addLayout(subjects_layout)
            
        # Add skill level rating if available
        if has_metadata and hasattr(self.lesson.metadata, 'skill_level') and self.lesson.metadata.skill_level is not None:
            # Create a container for the skill level
            skill_layout = QHBoxLayout()
            skill_layout.setSpacing(4)
            
            # Add a small label for "Difficulty:"
            difficulty_label = QLabel("Difficulty:")
            difficulty_label.setStyleSheet(f"color: {disabled_color.name()}; font-size: 10px;")
            skill_layout.addWidget(difficulty_label)
            
            star_rating = HorizontalStarRating(self.lesson.metadata.skill_level)
            star_rating.set_star_size(12)  # Smaller stars to fit in the card
            skill_layout.addWidget(star_rating)
            
            skill_layout.addStretch()
            layout.addLayout(skill_layout)
        
        # Add stretch to push content to the top
        layout.addStretch()
        
    def mousePressEvent(self, event):
        """Handle mouse press events to make the card clickable"""
        super().mousePressEvent(event)
        self.clicked.emit(self.lesson)
        
    def enterEvent(self, event):
        """Handle mouse enter events for hover effect"""
        super().enterEvent(event)
        self.setCursor(Qt.PointingHandCursor)
        
    def leaveEvent(self, event):
        """Handle mouse leave events for hover effect"""
        super().leaveEvent(event)
        self.setCursor(Qt.ArrowCursor)
