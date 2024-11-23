import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit,
                            QListWidget, QListWidgetItem)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class IconFinder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Icon Finder")
        self.resize(400, 600)
        
        # Create layout
        layout = QVBoxLayout()
        
        # Add search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search icons...")
        self.search_input.textChanged.connect(self.filter_icons)
        layout.addWidget(self.search_input)
        
        # Create list widget
        self.list = QListWidget()
        layout.addWidget(self.list)
        
        self.setLayout(layout)
        
        # Load all icons
        self.load_icons()
        
    def load_icons(self):
        """Load all available theme icons"""
        theme = QIcon.themeName()
        if not theme:
            theme = "hicolor"  # fallback theme
            
        for icon_name in QIcon.themeSearchPaths():
            theme_dir = f"{icon_name}/{theme}"
            if not os.path.exists(theme_dir):
                continue
                
            for root, _, files in os.walk(theme_dir):
                for file in files:
                    if file.endswith(('.png', '.svg')):
                        # Extract icon name without extension and size directory
                        icon_name = os.path.splitext(file)[0]
                        if QIcon.hasThemeIcon(icon_name):
                            item = QListWidgetItem(icon_name)
                            item.setIcon(QIcon.fromTheme(icon_name))
                            self.list.addItem(item)
            
    def filter_icons(self, filter_text):
        """Filter icons based on search text"""
        filter_text = filter_text.lower()
        for i in range(self.list.count()):
            item = self.list.item(i)
            item.setHidden(
                filter_text not in item.text().lower()
            )

def main():
    from PyQt5.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    finder = IconFinder()
    finder.show()
    return app.exec_()

if __name__ == "__main__":
    import sys
    sys.exit(main())
