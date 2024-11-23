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
    
    # Initialize translation
    translator = QTranslator()
    locale = QLocale()
    try:
        # First try package installation path
        import pkg_resources
        translations_dir = pkg_resources.resource_filename('welcome', 'translations')
    except (ImportError, pkg_resources.DistributionNotFound):
        # Fallback to local development path
        translations_dir = os.path.join(os.path.dirname(__file__), "translations")
    
    logger.info(f"Loading translations from: {translations_dir}")
    
    # Try loading translation in order of preference
    translation_loaded = False
    
    # First try full locale name (e.g. de_DE)
    if translator.load(locale, "welcome", "_", translations_dir):
        translation_loaded = True
    # Then try language only (e.g. de)
    elif translator.load(QLocale(locale.language()), "welcome", "_", translations_dir):
        translation_loaded = True
    # Finally try English as fallback
    elif locale.language() != QLocale.English and translator.load("welcome_en", translations_dir):
        translation_loaded = True
        
    if translation_loaded:
        app.installTranslator(translator)
        logger.info(f"Successfully loaded translation for locale: {locale.name()}")
        
        # Log some example translations to verify loading
        test_strings = [
            "Welcome!",
            "What grade are you in?",
            "German",
            "Foreign Language",
            "Mathematics"
        ]
        
        logger.info("Translation test pairs (English -> Translated):")
        for text in test_strings:
            translated = QApplication.translate("WelcomeWizard", text)
            logger.info(f"  '{text}' -> '{translated}'")
    else:
        logger.warning(f"No translation found for locale: {locale.name()}, using default English")
    
    # Create wizard after translator is set up
    wizard = WelcomeWizard()
    wizard.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
