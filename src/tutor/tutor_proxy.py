from typing import Optional
from venv import logger
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
    
    def open_tutor(self, unit: BaseLesson, force_new: bool = False, disable_program: bool = False) -> TutorView:
        """
        Open a tutor view for the given unit.
        If a view already exists, it will be brought to front.
        """

        if self._active_view and self._active_view.unit == unit and not force_new:
            self._active_view.show()
            return self._active_view


        if self._active_view:
            self.close_tutor()


        
        # Create new view
        self._active_view = TutorView(unit, disable_program=disable_program)
        self._active_view.show()
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
