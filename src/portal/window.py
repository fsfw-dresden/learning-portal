from PyQt5.QtWidgets import (QMainWindow, QWidget, QToolBar, 
                            QVBoxLayout, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from welcome.wizard import WelcomeWizard
from portal.content import ContentWidget

def tr(text: str) -> str:
    """Helper function for translations"""
    from PyQt5.QtWidgets import QApplication
    return QApplication.translate("Portal", text)

class PortalWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Schulstick Portal")
        self.resize(800, 600)
        
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
        
        # Add expanding spacer widget
        spacer = QWidget()
        spacer.setSizePolicy(1, 0)
        toolbar.addWidget(spacer)
        
        # Add settings button right-aligned
        settings_action = QAction(QIcon.fromTheme("preferences-system"), tr("Settings"), self)
        toolbar.addAction(settings_action)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.widgetForAction(settings_action).setLayoutDirection(Qt.RightToLeft)
        
        # Add content widget
        self.content = ContentWidget()
        layout.addWidget(self.content)
        
    def show_wizard(self):
        wizard = WelcomeWizard()
        wizard.exec_()
