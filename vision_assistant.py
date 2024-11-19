import anthropic
from PIL import Image
import io
from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

class VisionAssistant:
    def __init__(self):
        self.client = anthropic.Anthropic()
        
    def analyze_screenshot(self, screenshot_path, user_question):
        """
        Analyze a screenshot using Claude's computer vision capabilities
        and return guidance information
        """
        with open(screenshot_path, 'rb') as img_file:
            img_bytes = img_file.read()
            
        response = self.client.beta.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            tools=[{
                "type": "computer_20241022",
                "name": "computer",
                "display_width_px": 1024,
                "display_height_px": 768,
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
