import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtCore import Qt

def main():
    app = QApplication(sys.argv)
    window = QMainWindow()
    window.setWindowTitle("Hello World")
    window.setGeometry(100, 100, 280, 120)
    
    label = QLabel("Hello, World!", parent=window)
    label.setAlignment(Qt.AlignCenter)
    window.setCentralWidget(label)
    
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
