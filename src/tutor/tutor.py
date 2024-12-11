from enum import Enum
import logging
from PyQt5.QtWidgets import (QWidget, QPushButton, QApplication, QVBoxLayout, 
                            QHBoxLayout, QSizePolicy, QMenu, QAction,
                            QMessageBox, QCheckBox)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QUrl, QSize, QObject, pyqtSlot
from PyQt5.QtGui import QPainter, QColor, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebChannel import QWebChannel
import json
import subprocess
from pathlib import Path
from typing import Optional, Tuple
from core.models import BaseLesson, LessonMetadata, ViewMode, DockPosition, ScreenHint
from core.preferences import Preferences
from core.launcher import ProgramLauncher

# Translation context for all tutor pages
TRANSLATION_CONTEXT = "TutorView"

def tr(text: str, *args) -> str:
    """Helper function for translations with variable substitution"""
    translated = QApplication.translate(TRANSLATION_CONTEXT, text)
    if args:
        return translated % args
    return translated

class CollapseIcons:
    BOTTOM = ("▼", "▲")
    TOP = ("▲", "▼")
    LEFT = ("◀", "▶")
    RIGHT = ("▶", "◀")

class TutorView(QWidget):
    
    def __init__(self, unit: BaseLesson):
        super().__init__()
        self.unit = unit
        if isinstance(unit, LessonMetadata) and  unit.screen_hint != None:
            self.screen_hint = unit.screen_hint
        else:
            self.screen_hint = ScreenHint(position=DockPosition.RIGHT, mode=ViewMode.DOCKED)
        
        self.logger = logging.getLogger(__name__)
        self.current_url = None
        self.is_expanded = True
        self.position = DockPosition(self.screen_hint.position)
        self.mode = ViewMode(self.screen_hint.mode)
        
        # Context menu setup
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # Set window properties based on mode
        if self.mode == ViewMode.DOCKED:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
            self.setAttribute(Qt.WA_TranslucentBackground)
        else:
            self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # Get current screen based on mouse position
        cursor_pos = QApplication.desktop().cursor().pos()
        self.current_screen = QApplication.desktop().screenNumber(cursor_pos)
        
        # Create main layout based on position
        self.main_layout = QHBoxLayout() if self.position in [DockPosition.LEFT, DockPosition.RIGHT] else QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        
        # Create content widget
        self.content_widget = QWidget()
        self.content_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
            
        # Create web view with transparent background
        self.web_view = QWebEngineView()
        
        # Inject JavaScript to monitor navigation
        js_code = """
        // Load QWebChannel JavaScript library
        var script = document.createElement('script');
        script.src = 'qrc:///qtwebchannel/qwebchannel.js';
        script.onload = function() {
            // Initialize after library loads
            new QWebChannel(qt.webChannelTransport, function(channel) {
                window.handler = channel.objects.handler;
                
                // Set up hash change monitoring
                let lastHash = window.location.hash;
                function pollHash() {
                    if (window.location.hash !== lastHash) {
                        lastHash = window.location.hash;
                        try {
                            handler.handleMessage(JSON.stringify({
                                'type': 'urlChanged',
                                'url': window.location.href
                            }));
                        } catch (e) {
                            console.warn('Error sending message:', e);
                        }
                    }
                }
                
                // Start polling
                setInterval(pollHash, 500);
                
                // Send initial URL
                handler.handleMessage(JSON.stringify({
                    'type': 'urlChanged',
                    'url': window.location.href
                }));

                // Add click handler for external links
                document.addEventListener('click', function(e) {
                    let target = e.target;
                    // Find closest anchor tag if clicked element is not an anchor
                    while (target && target.tagName !== 'A') {
                        target = target.parentElement;
                    }
                    if (target && target.href && !target.href.startsWith(window.location.origin)) {
                        e.preventDefault();
                        handler.handleMessage(JSON.stringify({
                            'type': 'externalLink',
                            'url': target.href
                        }));
                    }
                }, true);
            });
        };
        document.head.appendChild(script);
        """
        
        # Create handler object for JavaScript messages
        class Handler(QObject):
            @pyqtSlot(str)
            def handleMessage(self, message):
                self.parent().handle_js_message(message)
                
        self.handler = Handler()
        self.handler.parent = lambda: self
        
        # Create web channel and expose handler
        self.channel = QWebChannel()
        self.channel.registerObject('handler', self.handler)
        self.web_view.page().setWebChannel(self.channel)
        
        # Add JavaScript injection after page loads
        self.web_view.loadFinished.connect(
            lambda ok: self.web_view.page().runJavaScript(js_code) if ok else None
        )
        
        self.web_view.page().setBackgroundColor(Qt.transparent)
        self.web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.web_view.customContextMenuRequested.connect(self.show_web_context_menu)
        
        self.content_layout.addWidget(self.web_view)
        
        if self.unit.tutorial_url:
            url = self.unit.tutorial_url
            if url is None:
                self.logger.error(f"Tutorial URL is not set for unit: {self.unit}")
                return
            initial_url = QUrl(url)
            self.web_view.load(initial_url)
            self.current_url = initial_url
            self.logger.info(f"Loading initial URL: {initial_url.toString()}")
        
        # Create and setup toggle button if in docked mode
        if self.mode == ViewMode.DOCKED:
            self.toggle_btn = QPushButton()
            self.toggle_btn.clicked.connect(self.toggle_expansion)
            self.setup_toggle_button()
            
            # Add widgets to main layout in correct order
            if self.position in [DockPosition.RIGHT, DockPosition.BOTTOM]:
                self.main_layout.addWidget(self.toggle_btn)
                self.main_layout.addWidget(self.content_widget)
            else:
                self.main_layout.addWidget(self.content_widget)
                self.main_layout.addWidget(self.toggle_btn)
        else:
            self.toggle_btn = None
            self.main_layout.addWidget(self.content_widget)
        
        # Initialize screen geometry and apply hints
        self.update_screen_geometry()
        self.apply_screen_hints()
        
        # Launch associated program if specified
        if isinstance(self.unit, LessonMetadata) and self.unit.program_launch_info:
            self.program_process = ProgramLauncher.launch_program(self.unit)

    def setup_toggle_button(self):
        """Setup the toggle button appearance and position"""
        if self.position in [DockPosition.LEFT, DockPosition.RIGHT]:
            self.toggle_btn.setFixedSize(20, 60)
        else:
            self.toggle_btn.setFixedSize(60, 20)
            
        self.toggle_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(60, 60, 60, 200);
                border: none;
                border-radius: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(80, 80, 80, 200);
            }
        """)
        self.update_toggle_button_icon()
        
    def update_toggle_button_icon(self):
        """Update toggle button icon based on position and state"""
        if not self.toggle_btn:
            return
            
        icons = getattr(CollapseIcons, self.position.value.upper())
        self.toggle_btn.setText(icons[0] if self.is_expanded else icons[1])
        
    def update_screen_geometry(self):
        """Update geometry based on current screen"""
        screen = QApplication.desktop().screenGeometry(self.current_screen)
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.screen_x = screen.x()
        self.screen_y = screen.y()
        
        # Setup animation
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

    def get_dimensions(self) -> Tuple[int, int]:
        """Calculate dimensions based on mode and hints"""
        if self.mode == ViewMode.FREE:
            width = min(int(self.screen_width * 0.7), self.screen_hint.preferred_width or self.screen_width)
            height = min(int(self.screen_height * 0.4), self.screen_hint.preferred_height or self.screen_height)
        else:
            if self.position in [DockPosition.LEFT, DockPosition.RIGHT]:
                width = min(self.screen_width // 3, self.screen_hint.preferred_width or self.screen_width)
                height = self.screen_height
            else:
                width = self.screen_width
                height = min(self.screen_height // 3, self.screen_hint.preferred_height or self.screen_height)
                
        return width, height
        
    def apply_screen_hints(self):
        """Apply screen positioning hints"""
        width, height = self.get_dimensions()
        self.expanded_size = QSize(width, height)
        
        # Set collapsed size based on orientation
        if self.mode == ViewMode.DOCKED:
            if self.position in [DockPosition.LEFT, DockPosition.RIGHT]:
                self.collapsed_size = QSize(30, height)
            else:
                self.collapsed_size = QSize(width, 30)
        
        # Calculate initial position
        if self.mode == ViewMode.FREE:
            x = self.screen_x + (self.screen_width - width) // 2
            y = self.screen_y + (self.screen_height - height) // 2
        else:
            if self.position == DockPosition.TOP:
                x = self.screen_x
                y = self.screen_y
            elif self.position == DockPosition.BOTTOM:
                x = self.screen_x
                y = self.screen_y + self.screen_height - height
            elif self.position == DockPosition.LEFT:
                x = self.screen_x
                y = self.screen_y
            else:  # RIGHT
                x = self.screen_x + self.screen_width - width
                y = self.screen_y
        
        self.setGeometry(x, y, width, height)

    def toggle_expansion(self):
        """Toggle between expanded and collapsed states"""
        if self.mode != ViewMode.DOCKED:
            return
            
        self.is_expanded = not self.is_expanded
        current_geo = self.geometry()
        
        if self.position in [DockPosition.LEFT, DockPosition.RIGHT]:
            new_width = self.expanded_size.width() if self.is_expanded else self.collapsed_size.width()
            if self.position == DockPosition.RIGHT:
                new_x = self.screen_x + self.screen_width - new_width
                new_rect = QRect(new_x, current_geo.y(), new_width, current_geo.height())
            else:
                new_rect = QRect(self.screen_x, current_geo.y(), new_width, current_geo.height())
        else:
            new_height = self.expanded_size.height() if self.is_expanded else self.collapsed_size.height()
            if self.position == DockPosition.BOTTOM:
                new_y = self.screen_y + self.screen_height - new_height
                new_rect = QRect(current_geo.x(), new_y, current_geo.width(), new_height)
            else:
                new_rect = QRect(current_geo.x(), self.screen_y, current_geo.width(), new_height)
        
        self.animation.setStartValue(current_geo)
        self.animation.setEndValue(new_rect)
        self.animation.start()
        
        self.update_toggle_button_icon()
        
    def paintEvent(self, event):
        if self.mode == ViewMode.DOCKED:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw semi-transparent background
            painter.fillRect(self.rect(), QColor(40, 40, 40, 200))

    def closeEvent(self, event):
        """Handle window close event"""
        if hasattr(self, 'program_process') and self.program_process:
            self.program_process.terminate()
        # Remove from proxy's active view
        from .tutor_proxy import TutorViewProxy
        proxy = TutorViewProxy.get_instance()
        proxy.remove_tutor(self.unit)
        super().closeEvent(event)

    def show_context_menu(self, pos):
        """Show the context menu for dock mode selection"""
        # Convert position to global coordinates for proper menu placement
        global_pos = self.mapToGlobal(pos)
        self.show_dock_menu(global_pos)

    def show_web_context_menu(self, pos):
        """Handle context menu events from the web view"""
        # Convert position to global coordinates
        global_pos = self.web_view.mapToGlobal(pos)
        self.show_dock_menu(global_pos)

    def show_dock_menu(self, global_pos):
        """Show the dock mode selection menu at the specified global position"""
        menu = QMenu(self)
        
        # Create actions for each dock mode
        actions = {
            (ViewMode.FREE, None): (QIcon.fromTheme("window"), tr("Undocked")),
            (ViewMode.DOCKED, DockPosition.LEFT): (QIcon.fromTheme("format-justify-left"), tr("Dock Left")),
            (ViewMode.DOCKED, DockPosition.RIGHT): (QIcon.fromTheme("format-justify-right"), tr("Dock Right")),
            (ViewMode.DOCKED, DockPosition.TOP): (QIcon.fromTheme("format-text-direction-vertical"), tr("Dock Top")),
            (ViewMode.DOCKED, DockPosition.BOTTOM): (QIcon.fromTheme("format-text-direction-vertical"), tr("Dock Bottom"))
        }
        
        for (mode, position), (icon, text) in actions.items():
            action = QAction(icon, text, self)
            action.setCheckable(True)
            action.setChecked(self.mode == mode and (mode == ViewMode.FREE or self.position == position))
            action.triggered.connect(lambda checked, m=mode, p=position: self.change_dock_mode(m, p))
            menu.addAction(action)

        menu.addSeparator()
        
        close_action = QAction(QIcon.fromTheme("window-close"), tr("Close"), self)
        close_action.triggered.connect(self.close)
        menu.addAction(close_action)
        
        menu.exec_(global_pos)
    
    def change_dock_mode(self, new_mode: ViewMode, new_position: Optional[DockPosition] = None):
        """Change the dock mode and position of the window by creating a new instance with overridden ScreenHint"""
        if new_mode == self.mode and (new_mode == ViewMode.FREE or new_position == self.position):
            return
            
        # Create a new unit with overridden screen hint
        modified_unit = self.unit
        modified_unit.screen_hint = ScreenHint(
            position=new_position or self.position,
            mode=new_mode,
            preferred_width=self.screen_hint.preferred_width,
            preferred_height=self.screen_hint.preferred_height
        )
        
        # Create new window with the modified unit using singleton pattern
        new_window = TutorView.get_instance(modified_unit)
        
        # Load the current URL if it exists
        if self.current_url:
            new_window.web_view.setUrl(self.current_url)
            
        new_window.show()
        
        # Close this window
        self.close()


    def handle_external_link(self, url: str) -> None:
        """Handle clicks on external links"""
        preferences = Preferences.load()
        
        if preferences.support.allow_external_links  and preferences.support.remember_external_links:
            # Open directly if allowed and remembered
            self.open_external_link(url)
            return
            
        if not preferences.support.remember_external_links:
            # Ask user if not previously allowed
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle(tr("External Link"))
            msg.setText(tr("Do you want to open this external link?"))
            msg.setInformativeText(url)
            
            # Add remember checkbox
            remember = QCheckBox(tr("Remember my choice"))
            msg.setCheckBox(remember)
            
            # Add custom buttons
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.No)
            
            if msg.exec_() == QMessageBox.Yes:
                preferences.support.allow_external_links = True
                if remember.isChecked():
                    preferences.support.remember_external_links = True
                preferences.save()
                self.open_external_link(url)
    
    def open_external_link(self, url: str) -> None:
        """Open URL in default browser using xdg-open"""
        try:
            subprocess.run(['xdg-open', url])
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to open URL: {e}")
            QMessageBox.critical(
                self,
                self.tr("Error"),
                self.tr("Failed to open external link: {url}").format(url=url)
            )

    def handle_js_message(self, message):
        """Handle messages from injected JavaScript"""
        try:
            data = json.loads(message)
            if data['type'] == 'urlChanged':
                self.current_url = QUrl(data['url'])
            elif data['type'] == 'externalLink':
                self.handle_external_link(data['url'])
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON message: {e}")
            self.logger.error(f"Raw message was: {message}")
