from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                            QFrame, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from core.models import SimpleLesson
from tutor.tutor import TutorView
from portal.tr import tr

class SimpleUnitCard(QFrame):
    def __init__(self, unit: SimpleLesson, parent=None):
        super().__init__(parent)
        self.unit = unit
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        self.setCursor(Qt.PointingHandCursor)
        self.tutor_view = None
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFixedSize(300, 350)  # Match UnitCard size
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
            QLabel#info {
                color: #b0b0b0;
                font-style: italic;
                margin: 4px 0;
            }
        """)
        
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Simple icon or placeholder
        icon_label = QLabel()
        icon_label.setPixmap(QIcon.fromTheme("text-x-generic").pixmap(128, 128))
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Title
        title = QLabel(self.unit.title)
        title.setObjectName("title")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Info about simple lesson
        info = QLabel(tr("No Metadata"))
        info.setObjectName("info")
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if not self.tutor_view:
                self.tutor_view = TutorView(self.unit)
            self.tutor_view.show()
