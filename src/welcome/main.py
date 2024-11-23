import sys
import os
import os.path
import logging
os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false;qt.*=false;*.warning=false'
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from welcome.wizard import WelcomeWizard

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Reduce Qt logging verbosity
    qt_logger = logging.getLogger('PyQt5')
    qt_logger.setLevel(logging.WARNING)
    
    # Reduce Qt logging verbosity
    qt_logger = logging.getLogger('PyQt5')
    qt_logger.setLevel(logging.WARNING)
    
    app = QApplication(sys.argv)
    
    # Create translator before any widgets
    translator = QTranslator()
    
    # Try to load translation using QLocale
    if translator.load(QLocale(), 
                      "welcome",  # base name
                      "_",        # separator 
                      os.path.join(os.path.dirname(__file__), "translations")):  # dir
        logger.info(f"Successfully loaded translation for locale: {QLocale().name()}")
        app.installTranslator(translator)
    else:
        logger.warning(f"Failed to load translation for locale: {QLocale().name()}")
    
    # Create wizard after translator is set up
    wizard = WelcomeWizard()
    wizard.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
