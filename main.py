import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton
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
        
        self.initUI()
        
    def initUI(self):
        self.setGeometry(100, 100, 200, 200)
        
        # Add background animation
        self.movie = QMovie("./cloud.webp")
        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()
        
        # Add text label
        self.label = QLabel("Hello,\nWorld!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white;")
        self.label.resize(200, 200)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Let mouse events pass through
        
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

def main():
    app = QApplication(sys.argv)
    window = CircularWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
