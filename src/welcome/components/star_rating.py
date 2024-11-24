from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QButtonGroup
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QIcon

class StarRating(QWidget):
    """A star rating widget that allows setting and getting ratings from 1-5"""
    
    ratingChanged = pyqtSignal(int)  # Signal emitted when rating changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rating = 0
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.star_group = QButtonGroup()
        
        for i in range(5):
            star_btn = QPushButton()
            star_btn.setCheckable(True)
            star_btn.setFixedSize(QSize(24, 24))
            star_btn.setIcon(QIcon.fromTheme("non-starred-symbolic"))
            star_btn.clicked.connect(lambda checked, rating=i+1: self.set_rating(rating))
            self.star_group.addButton(star_btn, i)
            layout.addWidget(star_btn)
    
    def set_rating(self, rating: int):
        """Set the rating (1-5) and update the star display"""
        self._rating = rating
        self._update_stars()
        self.ratingChanged.emit(rating)
    
    def rating(self) -> int:
        """Get the current rating"""
        return self._rating
    
    def _update_stars(self):
        """Update the star icons based on current rating"""
        for i, btn in enumerate(self.star_group.buttons()):
            btn.setIcon(QIcon.fromTheme(
                "starred-symbolic" if i < self._rating else "non-starred-symbolic"
            ))
