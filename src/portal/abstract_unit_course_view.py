from abc import abstractmethod
from PyQt5.QtWidgets import QWidget

class AbstractUnitCourseView(QWidget):
    """
    Abstract interface for unit and course view widgets.
    Ensures consistent implementation of reload functionality.
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    @abstractmethod
    def reload(self):
        """
        Reload the content of the view.
        This method must be implemented by all subclasses.
        """
        pass 