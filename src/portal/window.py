from PyQt5.QtWidgets import (QMainWindow, QWidget, QToolBar, 
                            QVBoxLayout, QAction, QSizePolicy)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from welcome.wizard import WelcomeWizard
from portal.unit_finder import UnitFinderWidget
from portal.unit_create_form import UnitCreateForm

def tr(text: str) -> str:
    """Helper function for translations"""
    from PyQt5.QtWidgets import QApplication
    return QApplication.translate("Portal", text)

class PortalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schulstick Portal")
        self.resize(1024, 768)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(toolbar)
        
        # Add home button
        home_action = QAction(QIcon.fromTheme("go-home"), tr("Home"), self)
        toolbar.addAction(home_action)
        
        # Add user button
        user_action = QAction(QIcon.fromTheme("system-users"), tr("User"), self)
        user_action.triggered.connect(self.show_wizard)
        toolbar.addAction(user_action)
        
        # Add expanding spacer to push settings to the right
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        toolbar.addWidget(spacer)
        
        # Add create new unit button
        create_action = QAction(QIcon.fromTheme("list-add"), tr("Create New Unit"), self)
        create_action.triggered.connect(self.show_create_form)
        toolbar.addAction(create_action)

        # Add reload button
        reload_action = QAction(QIcon.fromTheme("view-refresh"), tr("Reload Units"), self)
        reload_action.triggered.connect(self.reload_units)
        toolbar.addAction(reload_action)
        
        # Add settings button
        settings_action = QAction(QIcon.fromTheme("preferences-system"), tr("Settings"), self)
        toolbar.addAction(settings_action)
        
        # Add unit finder widget
        self.content = UnitFinderWidget()
        layout.addWidget(self.content)
        
    def show_wizard(self):
        wizard = WelcomeWizard()
        wizard.exec_()
        
    def show_create_form(self):
        form = UnitCreateForm(self)
        if form.exec_() == UnitCreateForm.Accepted:
            # We'll implement the actual creation in the next step
            pass
            
    def reload_units(self):
        """Reload all units by rescanning the collection"""
        self.content.load_units()
