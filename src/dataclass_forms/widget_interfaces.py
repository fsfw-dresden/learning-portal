"""
Common interfaces and base classes for dataclass form widgets.
"""

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget
from typing import List, TypeVar, Generic, Optional, Type, Any

T = TypeVar('T')

class FormWidgetInterface:
    """Interface for widgets that can be used in forms."""
    
    def get_value(self) -> Any:
        """Get the current value from the widget."""
        raise NotImplementedError("Subclasses must implement get_value")
    
    def set_value(self, value: Any) -> None:
        """Set the widget value."""
        raise NotImplementedError("Subclasses must implement set_value")

class ListWidgetBase(QWidget, Generic[T]):
    """Base class for widgets that edit lists of items."""
    
    valueChanged = pyqtSignal()
    
    def get_items(self) -> List[T]:
        """
        Get the current list of items.
        
        Returns:
            List of items
        """
        raise NotImplementedError("Subclasses must implement get_items")
    
    def set_items(self, items: List[T]) -> None:
        """
        Set the list of items.
        
        Args:
            items: List of items
        """
        raise NotImplementedError("Subclasses must implement set_items")
