from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit,
                            QScrollArea, QWidget, QGridLayout)
from PyQt5.QtCore import Qt, QTimer
from core.unit_scanner import UnitScanner
from portal.unit_card import UnitCard

class UnitFinderWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scanner = UnitScanner()
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        
        self.initUI()
        self.load_units()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        
        # Search field
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search units...")
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 14px;
            }
        """)
        layout.addWidget(self.search_input)
        
        # Scroll area for cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Container for cards
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(24)
        self.cards_layout.setContentsMargins(24, 24, 24, 24)
        scroll.setWidget(self.cards_container)
        
        layout.addWidget(scroll)
        
    def on_search_changed(self, text):
        """Debounce search to avoid too frequent updates"""
        self.search_timer.start(300)
        
    def perform_search(self):
        """Actually perform the search"""
        query = self.search_input.text()
        if query:
            units = self.scanner.search(query)
        else:
            units = self.scanner.list_all_lessons()
        self.display_units(units)
        
    def load_units(self):
        """Initial load of all units"""
        units = self.scanner.list_all_lessons()
        self.display_units(units)
        
    def display_units(self, units):
        """Clear and redisplay unit cards"""
        # Clear existing cards
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Add new cards
        for i, unit in enumerate(units):
            row = i // 3  # 3 cards per row
            col = i % 3
            card = UnitCard(unit)
            self.cards_layout.addWidget(card, row, col)
