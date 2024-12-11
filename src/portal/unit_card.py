from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QHBoxLayout, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from core.models import LessonMetadata
from tutor.tutor import TutorView
from tutor.tutor_proxy import TutorViewProxy
from portal.unit_context_menu import UnitContextMenu

class UnitCard(QFrame):
    def __init__(self, unit: LessonMetadata, parent=None):
        super().__init__(parent)
        self.unit = unit
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setCursor(Qt.PointingHandCursor)
        self.tutor_view = None
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFixedSize(300, 350)  # Set fixed size for all cards
        self.setStyleSheet("""
            QFrame {
                background-color: #2d2d2d;
                border-radius: 8px;
                padding: 12px;
                border: 1px solid #3d3d3d;
            }
            QLabel#title {
                font-size: 16px;
                font-weight: bold;
                color: white;
                margin-top: 8px;
            }
            QLabel#tag {
                background-color: #454545;
                color: #e0e0e0;
                border-radius: 4px;
                padding: 2px 6px;
                margin: 0 2px;
            }
            QLabel#skill {
                color: #b0b0b0;
                margin: 4px 0;
            }
        """)
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Preview image
        preview = QLabel()
        pixmap = QPixmap(str(self.unit.preview_path))
        preview.setPixmap(pixmap.scaled(276, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        preview.setAlignment(Qt.AlignCenter)
        layout.addWidget(preview)
        
        # Title
        title = QLabel(self.unit.title)
        title.setObjectName("title")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Skill level with stars
        skill_layout = QHBoxLayout()
        skill_label = QLabel("Skill Level:")
        skill_label.setObjectName("skill")
        skill_layout.addWidget(skill_label)
        
        # Add star icons using the same theme as StarRating
        for i in range(5):
            star_label = QLabel()
            star_label.setFixedSize(24, 24)  # Larger size for better visibility
            icon_name = "starred-symbolic" if i < self.unit.skill_level else "non-starred-symbolic"
            star_icon = QIcon.fromTheme(icon_name)
            star_label.setPixmap(star_icon.pixmap(24, 24))  # Scale pixmap to match size
            skill_layout.addWidget(star_label)
        
        skill_layout.addStretch()
        layout.addLayout(skill_layout)
        
        # Tags with fixed width
        tags_layout = QHBoxLayout()
        tags_layout.setSpacing(8)
        for tag in self.unit.tags[:3]:  # Show first 3 tags
            tag_label = QLabel(tag)
            tag_label.setObjectName("tag")
            tag_label.setFixedWidth(90)  # Fixed width for tags
            tag_label.setAlignment(Qt.AlignCenter)
            tags_layout.addWidget(tag_label)
        tags_layout.addStretch()
        layout.addLayout(tags_layout)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            TutorViewProxy.get_instance().open_tutor(self.unit)
        elif event.button() == Qt.RightButton:
            context_menu = UnitContextMenu(self.unit, self)
            context_menu.exec_(event.globalPos())
