from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLineEdit, 
                            QTreeWidget, QTreeWidgetItem)
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
        
        # Create tree widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Icon Name", "Preview"])
        self.tree.setColumnWidth(0, 250)
        layout.addWidget(self.tree)
        
        self.setLayout(layout)
        
        # Load all icons
        self.load_icons()
        
    def load_icons(self):
        """Load all available theme icons"""
        for icon_name in QIcon.themeSearchPaths():
            item = QTreeWidgetItem([icon_name])
            item.setIcon(0, QIcon.fromTheme(icon_name))
            self.tree.addTopLevelItem(item)
            
    def filter_icons(self, filter_text):
        """Filter icons based on search text"""
        filter_text = filter_text.lower()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            item.setHidden(
                filter_text not in item.text(0).lower()
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
