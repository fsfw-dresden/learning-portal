"""
Widget for editing a list of strings.
"""

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QHBoxLayout, QListWidget, QPushButton, QVBoxLayout, QWidget, QInputDialog
)

class StringListWidget(QWidget):
    """
    A widget for editing a list of strings with add/remove functionality.
    
    This widget provides a list view with buttons to add and remove items.
    It can be used standalone or integrated into forms.
    """
    
    valueChanged = pyqtSignal()
    
    def __init__(self, parent=None, items=None):
        """
        Initialize the string list widget.
        
        Args:
            parent: Parent widget
            items: Optional initial list of strings
        """
        super().__init__(parent)
        self._setup_ui()
        
        # Initialize with items if provided
        if items and hasattr(items, '__iter__'):
            for item in items:
                self.list_widget.addItem(str(item))
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create list widget
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
        
        # Add buttons for managing the list
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add", self)
        self.remove_button = QPushButton("Remove", self)
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.remove_button)
        layout.addLayout(buttons_layout)
        
        # Connect buttons
        self.add_button.clicked.connect(self._add_item)
        self.remove_button.clicked.connect(self._remove_selected_items)
        
        # Connect list widget signals
        self.list_widget.model().rowsInserted.connect(self.valueChanged.emit)
        self.list_widget.model().rowsRemoved.connect(self.valueChanged.emit)
    
    def _add_item(self):
        """Add a new item to the list using an input dialog."""
        text, ok = QInputDialog.getText(self, "Add Item", "Enter new item:")
        if ok and text:
            self.list_widget.addItem(text)
    
    def _remove_selected_items(self):
        """Remove all selected items from the list."""
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            for item in selected_items:
                self.list_widget.takeItem(self.list_widget.row(item))
    
    def get_items(self):
        """
        Get the current list of items.
        
        Returns:
            List of strings
        """
        items = []
        for i in range(self.list_widget.count()):
            items.append(self.list_widget.item(i).text())
        return items
    
    def set_items(self, items):
        """
        Set the list of items.
        
        Args:
            items: List of strings
        """
        self.list_widget.clear()
        if items and hasattr(items, '__iter__'):
            for item in items:
                self.list_widget.addItem(str(item))
        self.valueChanged.emit()
