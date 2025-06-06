import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, Qt
from core.translation import load_module_translations
from portal.window import PortalWindow
from portal.tr import tr

def main():
    logging.basicConfig(level=logging.INFO)
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Initialize translation using the TranslationManager
    load_module_translations("portal")
    
    window = PortalWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
