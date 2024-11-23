from PyQt5.QtWidgets import QWidget, QPushButton, QApplication, QVBoxLayout
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QUrl
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtWebEngineWidgets import QWebEngineView
import os
from vision_assistant.env_helper import EnvHelper

class TutorView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Get screen geometry
        screen = QApplication.primaryScreen().geometry()
        self.screen_width = screen.width()
        
        # Calculate dimensions
        self.expanded_width = self.screen_width // 3
        self.collapsed_width = 30
        self.is_expanded = True
        
        # Position window on right side of screen
        self.setGeometry(
            self.screen_width - self.expanded_width,
            0,
            self.expanded_width,
            screen.height()
        )
        
        # Create layout
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 0, 0)
        
        # Create web view with transparent background
        self.web_view = QWebEngineView(self)
        self.web_view.page().setBackgroundColor(Qt.transparent)
        calling_dir = os.getenv("PWD", os.getcwd())
        host = "https://tutor.schulstick.org" if EnvHelper.is_production() else "http://localhost:3000"
        application = "inkscape"
        unit = "lektion1"
        page = "intro"
       #tutorial_path = os.path.join(calling_dir, "tutor-next", "export", application, unit, page)
        external_path = os.path.join(host, application, unit, page)
        print(f"Loading tutorial from: {external_path}")
        self.web_view.load(QUrl(external_path))
        self.layout.addWidget(self.web_view)
        
        # Create toggle button
        self.toggle_btn = QPushButton("◀", self)
        self.toggle_btn.setFixedSize(20, 60)
        self.toggle_btn.clicked.connect(self.toggle_expansion)
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: none;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        self.update_button_position()
        
        # Setup animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)
        
    def update_button_position(self):
        """Update toggle button position based on expansion state"""
        self.toggle_btn.move(0, self.height() // 2 - 30)
        self.toggle_btn.setText("▶" if self.is_expanded else "◀")
        
    def toggle_expansion(self):
        """Toggle between expanded and collapsed states"""
        self.is_expanded = not self.is_expanded
        
        new_width = self.expanded_width if self.is_expanded else self.collapsed_width
        new_x = self.screen_width - new_width
        
        self.animation.setStartValue(self.geometry())
        self.animation.setEndValue(QRect(
            new_x,
            self.y(),
            new_width,
            self.height()
        ))
        
        self.animation.start()
        self.update_button_position()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw semi-transparent background
        painter.fillRect(self.rect(), QColor(40, 40, 40, 200))
