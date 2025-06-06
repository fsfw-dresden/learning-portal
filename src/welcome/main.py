import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView
from core.translation import load_module_translations
from welcome.wizard import WelcomeWizard
from welcome.tr import tr

def main():
    logging.basicConfig(level=logging.INFO)
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false;qt.*=false;qt.metadata.*=false'
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Initialize translation using the TranslationManager
    load_module_translations("welcome")
    
    wizard = WelcomeWizard()
    wizard.show()
    app.exec_()

    # Start portal main()
    from portal.main import main as portal_main
    return portal_main()

if __name__ == "__main__":
    sys.exit(main())
