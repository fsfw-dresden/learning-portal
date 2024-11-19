import os
import base64
import anthropic
from response_models import VisionResponse
from PIL import Image, UnidentifiedImageError
import io
from PyQt5.QtCore import QPoint, QRect, QTimer, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

class VisionAssistant:
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        self.client = anthropic.Anthropic(api_key=api_key)
        
    def analyze_screenshot(self, screenshot_path, user_question):
        """
        Analyze a screenshot using Claude's computer vision capabilities
        and return guidance information
        """
        try:
            # Get screenshot dimensions
            with Image.open(screenshot_path) as img:
                screen_width, screen_height = img.size
            
            # Read image bytes and convert to base64
            with open(screenshot_path, 'rb') as img_file:
                img_bytes = base64.b64encode(img_file.read()).decode('utf-8')
            
            response = self.client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=[{
                "type": "computer_20241022",
                "name": "computer",
                "display_width_px": screen_width,
                "display_height_px": screen_height,
                "display_number": 1,
            }],
            messages=[{
                "role": "user", 
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": img_bytes
                        }
                    },
                    {
                        "type": "text",
                        "text": f"Analyze this screenshot and help with: {user_question}. "
                               f"Return a JSON with these fields: "
                               f"'look_at_coordinates': [x,y], 'instructions': 'step by step guide'"
                    }
                ]
            }],
            betas=["computer-use-2024-10-22"],
        )
        
            return VisionResponse.from_claude_response(response.content[0].text)
            
        except UnidentifiedImageError:
            raise ValueError("Could not open or identify the screenshot image")
        except Exception as e:
            raise RuntimeError(f"Error during vision analysis: {str(e)}")

class HighlightOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.highlight_point = None
        self.last_highlight_point = None
        self.opacity = 1.0
        self.instructions = []
        self.last_instructions = []
        
        # Setup fade out animation
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(1000)  # 1 second fade
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_animation.finished.connect(self.hide)
        
        # Setup timer for auto-hide
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.start_fade_out)
        
    def set_highlight(self, point, instructions=None):
        """Set the point to highlight with a circle and display instructions"""
        self.highlight_point = QPoint(point[0], point[1])
        self.last_highlight_point = self.highlight_point
        self.instructions = instructions if instructions else []
        self.last_instructions = self.instructions
        self.setWindowOpacity(1.0)
        self.show()
        self.update()
        
        # Reset and start the hide timer
        self.hide_timer.stop()
        self.hide_timer.start(10000)  # 10 seconds
        
    def start_fade_out(self):
        """Start the fade out animation"""
        self.fade_animation.start()
        
    def show_last_hint(self):
        """Show the last shown hint again"""
        if self.last_highlight_point and self.last_instructions:
            self.highlight_point = self.last_highlight_point
            self.instructions = self.last_instructions
            self.setWindowOpacity(1.0)
            self.show()
            self.update()
            self.hide_timer.stop()
            self.hide_timer.start(10000)
        
    def paintEvent(self, event):
        if self.highlight_point:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw semi-transparent circle
            painter.setBrush(QColor(255, 255, 0, 80))
            painter.setPen(QColor(255, 255, 0, 150))
            radius = 30
            painter.drawEllipse(self.highlight_point, radius, radius)
            
            # Draw instructions
            if self.instructions:
                # Calculate text height first
                font = painter.font()
                font.setPointSize(10)
                painter.setFont(font)
                
                total_height = 0
                for instruction in self.instructions:
                    text_rect = QRect(0, 0, 290, 1000)  # Temporary rect for measurement
                    bound_rect = painter.boundingRect(text_rect, Qt.TextWordWrap, instruction)
                    total_height += bound_rect.height() + 5
                
                # Create semi-transparent background for text
                text_bg = QRect(self.highlight_point.x() + radius + 10,
                              self.highlight_point.y() - 30,
                              300, total_height + 20)  # Add padding
                painter.fillRect(text_bg, QColor(0, 0, 0, 128))
                
                # Draw text
                painter.setPen(QColor(255, 255, 255))
                y_offset = text_bg.y() + 10  # Initial padding
                for instruction in self.instructions:
                    text_rect = QRect(text_bg.x() + 5, y_offset, 290, 1000)
                    bound_rect = painter.drawText(text_rect, Qt.TextWordWrap, instruction)
                    y_offset += bound_rect.height() + 5
