from PyQt5.QtCore import QPoint, QRect, QTimer, Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor

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
