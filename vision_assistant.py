import os
import base64
import anthropic
from PIL import Image, UnidentifiedImageError
import io
from PyQt5.QtCore import QPoint, QRect
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
        
            return response.content
            
        except UnidentifiedImageError:
            raise ValueError("Could not open or identify the screenshot image")
        except Exception as e:
            raise RuntimeError(f"Error during vision analysis: {str(e)}")

class HighlightOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.highlight_point = None
        
    def set_highlight(self, point):
        """Set the point to highlight with a circle"""
        self.highlight_point = QPoint(point[0], point[1])
        self.update()
        
    def paintEvent(self, event):
        if self.highlight_point:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw semi-transparent circle
            painter.setBrush(QColor(255, 255, 0, 80))
            painter.setPen(QColor(255, 255, 0, 150))
            radius = 30
            painter.drawEllipse(self.highlight_point, radius, radius)
