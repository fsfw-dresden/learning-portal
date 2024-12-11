from typing import Optional, Dict
from PyQt5.QtCore import QObject
from .tutor import TutorView
from core.models import BaseLesson

class TutorViewProxy(QObject):
    """
    A proxy that manages TutorView instances.
    Implements the Virtual Proxy pattern to control access and lifecycle of TutorView windows.
    """
    _instance = None
    
    def __init__(self):
        super().__init__()
        self._active_views: Dict[str, TutorView] = {}
    
    @classmethod
    def get_instance(cls) -> 'TutorViewProxy':
        """Get the singleton proxy instance"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def open_tutor(self, unit: BaseLesson) -> TutorView:
        """
        Open a tutor view for the given unit.
        If a view already exists for this unit, it will be brought to front.
        """
        unit_id = str(unit.id)
        
        # Close existing view if present
        if unit_id in self._active_views:
            existing_view = self._active_views[unit_id]
            if not existing_view.isHidden():
                existing_view.activateWindow()
                existing_view.raise_()
                return existing_view
            else:
                existing_view.close()
                del self._active_views[unit_id]
        
        # Create new view
        view = TutorView(unit)
        self._active_views[unit_id] = view
        return view
    
    def close_tutor(self, unit_id: str) -> None:
        """Close the tutor view for the given unit"""
        if unit_id in self._active_views:
            self._active_views[unit_id].close()
            del self._active_views[unit_id]
    
    def close_all(self) -> None:
        """Close all active tutor views"""
        for view in list(self._active_views.values()):
            view.close()
        self._active_views.clear()
