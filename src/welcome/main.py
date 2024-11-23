import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from welcome.wizard import WelcomeWizard

def main():
    # Setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
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
