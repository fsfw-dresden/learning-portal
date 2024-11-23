import sys
import os
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
    
    # Setup translation
    translator = QTranslator()
    system_locale = QLocale.system()
    
    # Try to load system language first
    logger.info(f"Attempting to load translation for system locale: {system_locale.name()}")
    if not translator.load(system_locale, "de", "", ":/translations"):
        # If system language fails, fallback to German
        logger.info("Falling back to German translation")
        fallback_locale = QLocale(QLocale.German)
        if not translator.load(fallback_locale, "de", "", ":/translations"):
            logger.warning("Failed to load German translation")
    
    app.installTranslator(translator)
    
    wizard = WelcomeWizard()
    wizard.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
