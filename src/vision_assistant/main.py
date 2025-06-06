import sys
import os
import logging
import requests
from urllib.parse import urljoin
from urllib.parse import urljoin
import base64
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLineEdit,
                            QMenu, QAction, QSystemTrayIcon)
from PyQt5.QtCore import QBuffer, QByteArray
from core.assets import Assets
from core.preferences import Preferences
from portal.window import PortalWindow
from vision_assistant.vision import HighlightOverlay
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PyQt5.QtGui import (QPainter, QPainterPath, QColor, QIcon, QMovie, QPixmap)
from vision_assistant.tr import tr

os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false;qt.*=false;*.warning=false'
#maximize logging
#os.environ['QT_LOGGING_RULES'] = '*.debug=true;qt.qpa.*=true;qt.*=true;*.warning=true'

class CircularWindow(QWidget):
    def __init__(self):
        super().__init__()
        
        # Load translations for vision_assistant module when window is initialized
        from core.translation import load_module_translations
        load_module_translations("vision_assistant")
        
        self.porttal = None
        self.preferences = Preferences.load()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize API session
        self.base_url = os.getenv('VISION_API_URL', 'http://localhost:8000')
        self.api_key = os.getenv('VISION_API_KEY', 'development_key')
        self.session = requests.Session()
        self.session.headers.update({
            'X-API-KEY': self.api_key
        })
        
        # Create initial session
        try:
            response = self.session.post(urljoin(self.base_url, 'session'))
            response.raise_for_status()
            self.session_id = response.json()['session_id']
        except Exception as e:
            self.logger.error(f"Failed to create API session: {e}")
            self.session_id = None
        # Remove window decorations and make window stay on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        # Enable transparency
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Window state
        self.is_expanded = False
        self.circular_geometry = QRect(100, 100, 200, 200)
        self.expanded_geometry = QRect(100, 100, 600, 400)
        
        # Setup animations
        self.geometry_animation = QPropertyAnimation(self, b"geometry")
        self.geometry_animation.setDuration(300)
        self.geometry_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        self.initUI()
        self.setup_tray_icon()
        
    def setup_tray_icon(self):
        """Initialize system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme("applications-education"))
        
        # Create tray menu
        tray_menu = QMenu()
        show_action = QAction(tr("Show"), self)
        hide_action = QAction(tr("Hide"), self)
        quit_action = QAction(tr("Quit"), self)
        
        show_action.triggered.connect(self.show_from_tray)
        hide_action.triggered.connect(self.hide_to_tray)
        # Connect quit action to our cleanup method
        quit_action.triggered.connect(self.cleanup_and_quit)
        
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
    def show_from_tray(self):
        """Show window from system tray"""
        self.show()
        self.activateWindow()
        
    def hide_to_tray(self):
        """Hide window to system tray"""
        self.hide()
        
    def initUI(self):
        self.setGeometry(self.circular_geometry)
        

        # Add background animation for circular view
        try:
            self.movie = Assets.load_movie('cloud.webp', "vision_assistant")
        except Exception as e:
            self.logger.error(f"Failed to load movie: {e}")
            self.movie = QMovie()
            self.movie.setFileName('')  # Empty movie acts as black background

        self.movie.frameChanged.connect(self.repaint)
        self.movie.start()
        
        # Load static background for expanded view
        try:
            self.night_bg = Assets.load_pixmap('night.jpg', "vision_assistant")
        except Exception:
            self.night_bg = QPixmap()
        
        # Add search input
        self.search_input = QLineEdit(self)
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: transparent;
                border: 2px solid white;
                border-radius: 15px;
                padding: 5px 15px;
                color: white;
                selection-background-color: rgba(255, 255, 255, 50);
            }
        """)
        self.update_search_input_geometry()
        
        # Add search button
        self.search_btn = QPushButton("🔍", self)
        self.search_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: 2px solid white;
                border-radius: 15px;
                padding: 5px;
                color: white;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 50);
            }
        """)
        self.update_search_button_geometry()
        self.search_btn.clicked.connect(self.analyze_screenshot)
        
        # Create context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Create path based on window state
        path = QPainterPath()
        if self.is_expanded:
            path.addRoundedRect(0, 0, self.width(), self.height(), 20, 20)
        else:
            path.addEllipse(0, 0, self.width(), self.height())
        
        # Set up alpha mask composition
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        
        # Clear everything to transparent first
        painter.fillRect(self.rect(), Qt.transparent)
        
        painter.setClipPath(path)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        
        if self.is_expanded:
            # Draw static night background when expanded
            painter.drawPixmap(0, 0, self.night_bg.scaled(
                self.width(), self.height(),
                Qt.KeepAspectRatioByExpanding,
                Qt.SmoothTransformation
            ))
        else:
            # Draw animated cloud background when circular
            if self.movie and self.movie.currentPixmap():
                painter.drawPixmap(0, 0, self.movie.currentPixmap().scaled(
                    self.width(), self.height(),
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation
                ))
            
        # Use black as the alpha mask
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillPath(path, QColor(0, 0, 0, 180))  # Black controls opacity

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.oldPos = event.globalPos()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.pos())

    def show_context_menu(self, pos):
        """Show the context menu with screenshot and hint options"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(40, 40, 40, 240);
                border: 1px solid rgba(255, 255, 255, 30);
                border-radius: 5px;
                padding: 5px;
            }
            QMenu::item {
                color: white;
                padding: 5px 20px;
                border-radius: 3px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 30);
            }
        """)
        
        # Screenshot action
        screenshot_action = QAction(QIcon.fromTheme("camera-photo"), tr("Take Screenshot"), self)
        screenshot_action.triggered.connect(self.take_screenshot)
        menu.addAction(screenshot_action)
        
        # Show last hint action
        hint_action = QAction(QIcon.fromTheme("help-hint"), tr("Show Last Hint"), self)
        hint_action.triggered.connect(self.show_last_hint)
        menu.addAction(hint_action)
        
        # Toggle expand action
        expand_action = QAction(QIcon.fromTheme("view-fullscreen"),
                              tr("Expand Window") if not self.is_expanded else tr("Collapse Window"),
                              self)
        expand_action.triggered.connect(self.toggle_window_size)
        menu.addAction(expand_action)
        
        
        # Launch portal action
        portal_action = QAction(QIcon.fromTheme("applications-education"), tr("Open Portal"), self)
        portal_action.triggered.connect(self.launch_portal)
        menu.addAction(portal_action)
        
        # Add separator
        menu.addSeparator()
        
        # Close action
        close_action = QAction(QIcon.fromTheme("window-close"), tr("Close"), self)
        def close_sequence():
            menu.hide()  # Hide instead of close
            # Use singleShot timer to delay window close slightly
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(100, self.close)
        close_action.triggered.connect(close_sequence)
        menu.addAction(close_action)
        
        # Calculate menu position to be horizontally centered
        menu_pos = self.mapToGlobal(pos)
        menu_pos.setX(menu_pos.x() - menu.sizeHint().width() // 2)
        
        menu.exec_(menu_pos)

    def update_screen_geometry(self):
        """Update geometry based on current screen"""
        screen = QApplication.desktop().screenGeometry(self.current_screen)
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.screen_x = screen.x()
        self.screen_y = screen.y()
        
        # Update window position to stay within new screen bounds
        if not self.screen_hint or self.screen_hint.mode == "free":
            new_x = max(self.screen_x, min(self.x(), 
                       self.screen_x + self.screen_width - self.width()))
            new_y = max(self.screen_y, min(self.y(), 
                       self.screen_y + self.screen_height - self.height()))
            self.move(new_x, new_y)
        else:
            # Re-apply docked position
            self.apply_screen_hints()

    def apply_screen_hints(self):
        """Apply screen positioning and sizing hints"""
        # Set default dimensions
        self.expanded_width = self.screen_width // 3
        self.collapsed_width = 30
        self.is_expanded = True
        
        # Apply size hints if provided
        if self.screen_hint.preferred_width:
            self.expanded_width = min(self.screen_hint.preferred_width, self.screen_width)
            
        if self.screen_hint.preferred_height:
            height = min(self.screen_hint.preferred_height, self.screen_height)
            self.setFixedHeight(height)
        else:
            self.setFixedHeight(self.screen_height)
            
        if self.screen_hint.preferred_aspect and not (self.screen_hint.preferred_width and self.screen_hint.preferred_height):
            if self.screen_hint.preferred_width:
                height = int(self.screen_hint.preferred_width / self.screen_hint.preferred_aspect)
                self.setFixedHeight(min(height, self.screen_height))
            elif self.screen_hint.preferred_height:
                width = int(self.screen_hint.preferred_height * self.screen_hint.preferred_aspect)
                self.expanded_width = min(width, self.screen_width)
        
        # Position window based on screen hint position
        if self.screen_hint.position == "top":
            self.setGeometry(
                self.screen_x + (self.screen_width - self.expanded_width) // 2,
                self.screen_y,
                self.expanded_width,
                self.height()
            )
        elif self.screen_hint.position == "bottom":
            self.setGeometry(
                self.screen_x + (self.screen_width - self.expanded_width) // 2,
                self.screen_y + self.screen_height - self.height(),
                self.expanded_width,
                self.height()
            )
        elif self.screen_hint.position == "left":
            self.setGeometry(
                self.screen_x,
                self.screen_y + (self.screen_height - self.height()) // 2,
                self.expanded_width,
                self.height()
            )
        else:  # Default to right if no position or position is "right"
            self.setGeometry(
                self.screen_x + self.screen_width - self.expanded_width,
                self.screen_y,
                self.expanded_width,
                self.height()
            )
                         
    def update_screen_geometry(self):
        """Update geometry based on current screen"""
        screen = QApplication.desktop().screenGeometry(self.current_screen)
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        self.screen_x = screen.x()
        self.screen_y = screen.y()
        
        # Update window position to stay within new screen bounds
        if not self.screen_hint or self.screen_hint.mode == "free":
            new_x = max(self.screen_x, min(self.x(), 
                       self.screen_x + self.screen_width - self.width()))
            new_y = max(self.screen_y, min(self.y(), 
                       self.screen_y + self.screen_height - self.height()))
            self.move(new_x, new_y)
        else:
            # Re-apply docked position
            self.apply_screen_hints()
        
    def mouseMoveEvent(self, event):
        # Only allow movement in free mode
        if self.screen_hint and self.screen_hint.mode != "free":
            return
            
        # Check if we've moved to a different screen
        new_screen = QApplication.desktop().screenNumber(event.globalPos())
        if new_screen != self.current_screen:
            self.current_screen = new_screen
            self.update_screen_geometry()
            
        delta = event.globalPos() - self.oldPos
        new_pos = self.pos() + delta
        
        # Ensure window stays within screen bounds
        new_x = max(self.screen_x, min(new_pos.x(), 
                   self.screen_x + self.screen_width - self.width()))
        new_y = max(self.screen_y, min(new_pos.y(), 
                   self.screen_y + self.screen_height - self.height()))
        
        self.move(new_x, new_y)
        self.oldPos = event.globalPos()
        
    def toggle_window_size(self):
        """Toggle between circular and expanded rectangular window"""
        self.is_expanded = not self.is_expanded
        
        # Setup animation
        self.geometry_animation.setStartValue(self.geometry())
        target_geometry = self.expanded_geometry if self.is_expanded else self.circular_geometry
        self.geometry_animation.setEndValue(target_geometry)
        
        # Start animation
        self.geometry_animation.start()
        
        # Update UI elements
        self.update_search_input_geometry()
        self.update_search_button_geometry()
        
    def update_search_input_geometry(self):
        """Update search input size and position based on window state"""
        if self.is_expanded:
            self.search_input.setGeometry(20, 20, 500, 60)
            self.search_input.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        else:
            self.search_input.setGeometry(20, 85, 120, 30)
            self.search_input.setAlignment(Qt.AlignLeft)
        
    def update_search_button_geometry(self):
        """Update search button size and position based on window state"""
        if self.is_expanded:
            self.search_btn.setGeometry(530, 20, 50, 60)
        else:
            self.search_btn.setGeometry(150, 85, 30, 30)
        
    def take_screenshot(self):
        self.logger.info("Taking screenshot...")
        screen = QApplication.primaryScreen()
        screenshot = screen.grabWindow(0)
        screenshot.save("shot01.png")
        self.logger.info("Screenshot saved as shot01.png")
        
    def show_last_hint(self):
        """Show the last hint if available"""
        if hasattr(self, 'highlight_overlay'):
            self.highlight_overlay.show_last_hint()
            
    def launch_portal(self):
        """Launch the portal application"""
        if not self.porttal:
            self.porttal = PortalWindow()
        self.porttal.show()
    
    def cleanup_session(self):
        """Clean up API session on close"""
        if self.session_id:
            try:
                response = self.session.delete(
                    urljoin(self.base_url, f'session/{self.session_id}')
                )
                response.raise_for_status()
                self.logger.info("Successfully cleaned up API session")
            except Exception as e:
                self.logger.error(f"Error cleaning up API session: {e}")
    
    def cleanup_and_quit(self):
        """Clean up resources and quit the application"""
        # Clean up API session
        self.cleanup_session()
        
        # Unload translations
        from core.translation import unload_module_translations
        unload_module_translations("vision_assistant")
        
        # Quit the application
        QApplication.quit()
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.ignore()
        self.hide_to_tray()
            
    def analyze_screenshot(self):
        question = self.search_input.text()
        if not question:
            self.logger.warning("No search query provided")
            return
            
        try:
            self.logger.info(f"Sending prompt to API: {question}")
            
            # Take screenshot and encode as base64
            screen = QApplication.primaryScreen()
            screenshot = screen.grabWindow(0)
            
            # Save to bytes buffer and convert to base64
            buffer = QByteArray()
            buffer_device = QBuffer(buffer)
            buffer_device.open(QBuffer.WriteOnly)
            screenshot.save(buffer_device, "PNG")
            screenshot_b64 = base64.b64encode(buffer.data()).decode()
            
            # Send to API
            data = {
                'screenshot': screenshot_b64,
                'question': question
            }
            response = self.session.post(
                urljoin(self.base_url, f'vision/{self.session_id}'),
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"Vision analysis response: {result}")
            
            # Create and show highlight overlay
            if not hasattr(self, 'highlight_overlay'):
                self.highlight_overlay = HighlightOverlay()
            
            # Get screen geometry to position overlay
            screen = QApplication.primaryScreen()
            screen_geometry = screen.geometry()
            self.highlight_overlay.setGeometry(screen_geometry)
            
            # Show the highlight at the specified coordinates with instructions
            self.highlight_overlay.set_highlight(
                result['look_at_coordinates'],
                result['instructions']
            )
            
        except Exception as e:
            self.logger.error(f"Error during vision analysis: {e}")

def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Initialize translation using the TranslationManager
    from core.translation import load_module_translations
    load_module_translations("vision_assistant")
    window = CircularWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
