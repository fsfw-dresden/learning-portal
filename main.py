import sys
import os
import logging
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QLineEdit,
                            QMenu, QAction)
from vision_assistant import VisionAssistant, HighlightOverlay
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import (QPainter, QPainterPath, QColor, QMovie, QRegion,
                        QScreen, QIcon)


class CircularWindow(QWidget):
    def __init__(self):
        super().__init__()
        # Remove window decorations and make window stay on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
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
        
        # Create context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
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
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())

    def show_context_menu(self, pos):
        """Show the context menu with screenshot and hint options"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(40, 40, 40, 240);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                color: white;
                padding: 5px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 30);
            }
        """)
        
        # Screenshot action
        screenshot_action = QAction(QIcon.fromTheme("camera-photo"), "Take Screenshot", self)
        screenshot_action.triggered.connect(self.take_screenshot)
        menu.addAction(screenshot_action)
        
        # Show last hint action
        hint_action = QAction(QIcon.fromTheme("help-hint"), "Show Last Hint", self)
        hint_action.triggered.connect(self.show_last_hint)
        menu.addAction(hint_action)
        
        # Calculate menu position to be horizontally centered
        menu_pos = self.mapToGlobal(pos)
        menu_pos.setX(menu_pos.x() - menu.sizeHint().width() // 2)
        
        menu.exec_(menu_pos)

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
        
    def take_screenshot(self):
        self.logger.info("Taking screenshot...")
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        screenshot.save("shot01.png")
        self.logger.info("Screenshot saved as shot01.png")
        
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
            self.logger.info(f"Sending prompt to AI: {question}")
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
