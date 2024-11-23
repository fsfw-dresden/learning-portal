import os
import base64
import anthropic
from vision_assistant.models import VisionResponse
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
        self.scale_factor = 1  # Store scaling factor for coordinate translation
        
    def _get_scale_factor(self, width: int, height: int) -> int:
        """Determine optimal scaling factor for high resolution displays"""
        target_width = 1920  # Target width for reasonable resolution
        
        if width <= target_width:
            return 1
            
        # Find the smallest factor (2, 3, or 4) that gets us close to target
        for factor in [2, 3, 4]:
            if width / factor <= target_width:
                return factor
        
        return 4  # Max scale factor if still too large
        
    def analyze_screenshot(self, screenshot_path, user_question):
        """
        Analyze a screenshot using Claude's computer vision capabilities
        and return guidance information
        """
        try:
            # Open and potentially resize the image
            with Image.open(screenshot_path) as img:
                original_width, original_height = img.size
                self.scale_factor = self._get_scale_factor(original_width, original_height)
                
                if self.scale_factor > 1:
                    new_size = (
                        original_width // self.scale_factor,
                        original_height // self.scale_factor
                    )
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    
                # Convert to bytes
                img_buffer = io.BytesIO()
                img.save(img_buffer, format='PNG')
                img_bytes = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
                screen_width, screen_height = img.size
            
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
        
            # Get response and scale coordinates back up if needed
            vision_response = VisionResponse.from_claude_response(response.content[0].text)
            if self.scale_factor > 1:
                vision_response.look_at_coordinates = [
                    coord * self.scale_factor for coord in vision_response.look_at_coordinates
                ]
            return vision_response
            
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
                # Ensure instructions is a list
                if not isinstance(self.instructions, list):
                    self.instructions = [self.instructions]
                # Set up text formatting
                font = painter.font()
                font.setPointSize(10)
                font.setWeight(75)  # Make text slightly bold
                painter.setFont(font)
                
                # Fixed width for text block
                text_width = 300
                padding = 15
                
                # Calculate total height needed
                total_height = padding
                for instruction in self.instructions:
                    text_rect = QRect(0, 0, text_width - (padding * 2), 1000)
                    bound_rect = painter.boundingRect(text_rect, Qt.TextWordWrap | Qt.AlignLeft, instruction)
                    total_height += bound_rect.height() + padding
                
                # Position the text block
                block_x = self.highlight_point.x() + radius + 20
                block_y = int(self.highlight_point.y() - (total_height / 2))
                
                # Draw background with rounded corners
                text_bg = QRect(int(block_x), block_y, int(text_width), int(total_height))
                painter.setPen(Qt.NoPen)
                painter.setBrush(QColor(0, 0, 0, 180))
                painter.drawRoundedRect(text_bg, 10, 10)
                
                # Draw text
                painter.setPen(QColor(255, 255, 255))
                y_pos = block_y + padding
                for instruction in self.instructions:
                    text_rect = QRect(block_x + padding, y_pos, 
                                    text_width - (padding * 2), 1000)
                    bound_rect = painter.drawText(text_rect, 
                                               Qt.TextWordWrap | Qt.AlignLeft | Qt.TextJustificationForced,
                                               instruction)
                    y_pos += bound_rect.height() + padding
