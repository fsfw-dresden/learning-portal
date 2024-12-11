from typing import Optional, Type
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QWidget
from core.models import BaseLesson

class TutorViewProxy(QObject):
    """
    A proxy that manages a single TutorView instance.
    """
    _instance = None
    
    def __init__(self):
        super().__init__()
        self._active_view: Optional[QWidget] = None
        self._view_class: Optional[Type[QWidget]] = None
    
    @classmethod
    def get_instance(cls) -> 'TutorViewProxy':
        """Get the singleton proxy instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_view_class(self, view_class: Type[QWidget]) -> None:
        """Register the TutorView class to avoid circular imports"""
        self._view_class = view_class

    def open_tutor(self, unit: BaseLesson) -> QWidget:
        """
        Open a tutor view for the given unit.
        If a view already exists, it will be brought to front.
        """

        if self._active_view and self._active_view.unit == unit:
            self._active_view.show()
            return self._active_view

        if self._active_view:
            self.close_tutor()

        
        # Create new view
        if not self._view_class:
            raise RuntimeError("TutorView class not registered")
            
        self._active_view = self._view_class(unit)
        self._active_view.show()
        
        # Connect close event
        self._active_view.destroyed.connect(lambda: self.remove_tutor(unit))
        
        return self._active_view

    def remove_tutor(self, unit: BaseLesson) -> None:
        """Remove the tutor view for the given unit"""
        if self._active_view and self._active_view.unit == unit:
            self._active_view = None

    def close_tutor(self) -> None:
        """Close the active tutor view"""
        if self._active_view:
            self._active_view.close()
            self._active_view = None
