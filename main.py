import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QMovie

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
        self.movie_label = QLabel(self)
        self.movie_label.setMovie(self.movie)
        self.movie_label.resize(200, 200)
        self.movie.start()
        
        # Add text label
        self.label = QLabel("Hello,\nWorld!", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white;")
        self.label.resize(200, 200)
        self.label.setAttribute(Qt.WA_TransparentForMouseEvents)  # Let mouse events pass through
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create circular path
        path = QPainterPath()
        path.addEllipse(0, 0, self.width(), self.height())
        
        # Set semi-transparent overlay
        painter.fillPath(path, QColor(0, 0, 0, 120))  # RGBA: Black with 47% opacity

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = event.globalPos() - self.oldPos
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

def main():
    app = QApplication(sys.argv)
    window = CircularWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
