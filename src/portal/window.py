from PyQt5.QtWidgets import (QMainWindow, QWidget, QToolBar, 
                            QVBoxLayout, QAction, QSizePolicy, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from welcome.wizard import WelcomeWizard
from portal.unit_finder import UnitFinderWidget
from portal.course_browser import UnitBrowserWidget
from portal.unit_create_form import UnitCreateForm
from portal.abstract_unit_course_view import AbstractUnitCourseView

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
        
        # Add view switcher buttons
        self.finder_action = QAction(QIcon.fromTheme("edit-find"), tr("Unit Finder"), self)
        self.finder_action.setCheckable(True)
        self.finder_action.setChecked(True)
        self.finder_action.triggered.connect(self.show_unit_finder)
        toolbar.addAction(self.finder_action)
        
        self.browser_action = QAction(QIcon.fromTheme("view-list-icons"), tr("Unit Browser"), self)
        self.browser_action.setCheckable(True)
        self.browser_action.triggered.connect(self.show_unit_browser)
        toolbar.addAction(self.browser_action)
        
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
        
        # Create stacked widget to hold different views
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Add unit finder widget
        self.unit_finder = UnitFinderWidget()
        self.stacked_widget.addWidget(self.unit_finder)
        
        # Add unit browser widget
        self.unit_browser = UnitBrowserWidget()
        self.stacked_widget.addWidget(self.unit_browser)
        
        # Set unit finder as default view
        self.stacked_widget.setCurrentWidget(self.unit_finder)
        
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
        current_widget = self.stacked_widget.currentWidget()
        if isinstance(current_widget, AbstractUnitCourseView):
            current_widget.reload()
    
    def show_unit_finder(self):
        """Switch to unit finder view"""
        self.stacked_widget.setCurrentWidget(self.unit_finder)
        self.finder_action.setChecked(True)
        self.browser_action.setChecked(False)
    
    def show_unit_browser(self):
        """Switch to unit browser view"""
        self.stacked_widget.setCurrentWidget(self.unit_browser)
        self.finder_action.setChecked(False)
        self.browser_action.setChecked(True)
