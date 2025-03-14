from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class HorizontalStarRating(QWidget):
    """
    A widget that displays a star rating (0-10) using system theme icons.
    The rating is visualized with 5 stars that can be filled, half-filled, or empty.
    """
    
    def __init__(self, rating=0, parent=None):
        """
        Initialize the star rating widget.
        
        Args:
            rating (float): A number between 0 and 10 representing the rating
            parent: The parent widget
        """
        super().__init__(parent)
        self._rating = max(0, min(10, rating))  # Clamp between 0 and 10
        self._star_labels = []
        
        # Initialize UI
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(2)
        
        # Create the star labels
        for i in range(5):
            label = QLabel()
            label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
            self._layout.addWidget(label)
            self._star_labels.append(label)
        
        # Set the initial rating
        self.set_rating(self._rating)
    
    def set_rating(self, rating):
        """
        Set the rating value and update the star display.
        
        Args:
            rating (float): A number between 0 and 10
        """
        self._rating = max(0, min(10, rating))  # Clamp between 0 and 10
        
        # Convert 0-10 scale to 0-5 stars
        stars = self._rating / 2.0
        
        # Update each star icon
        for i in range(5):
            if stars >= i + 1:
                # Full star
                icon = QIcon.fromTheme("starred-symbolic", QIcon.fromTheme("starred"))
            elif stars > i:
                # Half star
                icon = QIcon.fromTheme("semi-starred-symbolic", QIcon.fromTheme("semi-starred"))
            else:
                # Empty star
                icon = QIcon.fromTheme("non-starred-symbolic", QIcon.fromTheme("non-starred"))
            
            # Set the icon to the label
            pixmap = icon.pixmap(16, 16)
            if not pixmap.isNull():
                self._star_labels[i].setPixmap(pixmap)
            else:
                # Fallback if theme icons are not available
                self._star_labels[i].setText("★" if stars >= i + 1 else "☆")
    
    def rating(self):
        """
        Get the current rating value.
        
        Returns:
            float: The current rating (0-10)
        """
        return self._rating
    
    def set_star_size(self, size):
        """
        Set the size of the star icons.
        
        Args:
            size (int): The size in pixels
        """
        for i in range(5):
            if i < len(self._star_labels):
                label = self._star_labels[i]
                icon_name = ""
                actual_size = size
                
                # Determine which icon is currently shown
                if self._rating / 2.0 >= i + 1:
                    icon_name = "starred-symbolic"
                elif self._rating / 2.0 > i:
                    icon_name = "semi-starred-symbolic"
                    actual_size = int(size * 1.4)  # Make semi-star slightly larger, for some reason the icon is too small (TODO: check if depends on the theme)
                else:
                    icon_name = "non-starred-symbolic"
                
                # Update with new size
                icon = QIcon.fromTheme(icon_name)
                pixmap = icon.pixmap(actual_size, actual_size)
                if not pixmap.isNull():
                    label.setPixmap(pixmap)
                    label.setFixedSize(size, size)  # Keep container size consistent