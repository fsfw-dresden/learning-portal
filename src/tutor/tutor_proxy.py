from typing import Optional
from PyQt5.QtCore import QObject
from .tutor import TutorView
from core.models import BaseLesson

class TutorViewProxy(QObject):
    """
    A proxy that manages a single TutorView instance.
    """
    _instance = None
    
    def __init__(self):
        super().__init__()
        self._active_view: Optional[TutorView] = None
    
    @classmethod
    def get_instance(cls) -> 'TutorViewProxy':
        """Get the singleton proxy instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def open_tutor(self, unit: BaseLesson) -> TutorView:
        """
        Open a tutor view for the given unit.
        If a view already exists, it will be brought to front.
        """
        # If there's an active view, bring it to front
        if self._active_view and not self._active_view.isHidden():
            self._active_view.activateWindow()
            self._active_view.raise_()
            return self._active_view
        
        # Create new view
        self._active_view = TutorView(unit)
        return self._active_view
    
    def close_tutor(self) -> None:
        """Close the active tutor view"""
        if self._active_view:
            self._active_view.close()
            self._active_view = None
