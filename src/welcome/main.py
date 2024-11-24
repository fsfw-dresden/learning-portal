import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, Qt
from welcome.wizard import WelcomeWizard

def main():
    logging.basicConfig(level=logging.INFO)
    os.environ['QT_LOGGING_RULES'] = '*.debug=false;qt.qpa.*=false;qt.*=false;qt.metadata.*=false'
    
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    # Initialize translation
    translator = QTranslator()
    locale = QLocale()
    
    try:
        import pkg_resources
        translations_dir = pkg_resources.resource_filename('welcome', 'translations')
    except (ImportError, pkg_resources.DistributionNotFound):
        translations_dir = os.path.join(os.path.dirname(__file__), "translations")
    
    # Try loading translations in order of preference
    if (translator.load(locale, "welcome", "_", translations_dir) or
        translator.load(QLocale(locale.language()), "welcome", "_", translations_dir) or
        (locale.language() != QLocale.English and translator.load("welcome_en", translations_dir))):
        app.installTranslator(translator)
    
    wizard = WelcomeWizard()
    wizard.show()
    return app.exec_()
if __name__ == "__main__":
    sys.exit(main())
