from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from portal.tr import tr


class ContentWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        
        # Placeholder label
        placeholder = QLabel(tr("Portal Content - Coming Soon"))
        placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(placeholder)
