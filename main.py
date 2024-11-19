import sys
import os
import logging
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit
from vision_assistant import VisionAssistant, HighlightOverlay
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (QPainter, QPainterPath, QColor, QMovie, QRegion,
                        QScreen)


class CircularWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Remove window decorations
        self.setWindowFlags(Qt.FramelessWindowHint)
        # Enable transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize vision assistant
        try:
            self.vision_assistant = VisionAssistant()
        except ValueError as e:
            self.logger.error(f"Failed to initialize VisionAssistant: {e}")
            self.vision_assistant = None
            
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 200, 200)
        
        # Add background animation
        self.movie = QMovie("./cloud.webp")
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()
        
        # Add search input
        self.search_input = QLineEdit(self)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: 2px solid white;
                border-radius: 15px;
                padding: 5px 15px;
                color: white;
                selection-background-color: rgba(255, 255, 255, 50);
            }
        """)
        self.search_input.resize(120, 30)
        self.search_input.move(20, 85)
        
        # Add search button
        self.search_btn = QPushButton("🔍", self)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid white;
                border-radius: 15px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)
        self.search_btn.resize(30, 30)
        self.search_btn.move(150, 85)
        self.search_btn.clicked.connect(self.analyze_screenshot)
        
        # Add screenshot button
        self.screenshot_btn = QPushButton("📸", self)
        self.screenshot_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                border: none;
                border-radius: 10px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        self.screenshot_btn.move(10, 10)
        self.screenshot_btn.clicked.connect(self.take_screenshot)
        
        # Add show last hint button
        self.show_hint_btn = QPushButton("💡", self)
        self.show_hint_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 100);
                border: none;
                border-radius: 10px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 150);
            }
        """)
        self.show_hint_btn.move(45, 10)
        self.show_hint_btn.clicked.connect(self.show_last_hint)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create circular path
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        
        # Set up alpha mask composition
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        
        # Clear everything to transparent first
        painter.fillRect(self.rect(), Qt.transparent)
        
        # Draw the current movie frame within the clip path
        if self.movie and self.movie.currentPixmap():
            painter.setClipPath(path)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawPixmap(0, 0, self.movie.currentPixmap().scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            ))
            
        # Use black as the alpha mask
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillPath(path, QColor(0, 0, 0, 180))  # Black controls opacity

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        
    def take_screenshot(self):
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        screenshot.save("shot01.png")
        
    def show_last_hint(self):
        """Show the last hint if available"""
        if hasattr(self, 'highlight_overlay'):
            self.highlight_overlay.show_last_hint()
            
    def analyze_screenshot(self):
        if not self.vision_assistant:
            self.logger.error("Vision Assistant not initialized")
            return
            
        question = self.search_input.text()
        if not question:
            self.logger.warning("No search query provided")
            return
            
        try:
            response = self.vision_assistant.analyze_screenshot("shot01.png", question)
            self.logger.info(f"Vision analysis response: {response}")
            
            # Create and show highlight overlay
            if not hasattr(self, 'highlight_overlay'):
                self.highlight_overlay = HighlightOverlay()
            
            # Get screen geometry to position overlay
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            self.highlight_overlay.setGeometry(screen_geometry)
            
            # Show the highlight at the specified coordinates with instructions
            self.highlight_overlay.set_highlight(response.look_at_coordinates, response.instructions)
            
        except Exception as e:
            self.logger.error(f"Error during vision analysis: {e}")

def main():
    app = QApplication(sys.argv)
    window = CircularWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
