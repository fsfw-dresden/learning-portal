import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, Qt
from portal.window import PortalWindow

def main():
    logging.basicConfig(level=logging.INFO)
    
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
        translations_dir = pkg_resources.resource_filename('portal', 'translations')
    except (ImportError, pkg_resources.DistributionNotFound):
        translations_dir = os.path.join(os.path.dirname(__file__), "translations")
    
    # Try loading translations in order of preference
    if (translator.load(locale, "portal", "_", translations_dir) or
        translator.load(QLocale(locale.language()), "portal", "_", translations_dir) or
        (locale.language() != QLocale.English and translator.load("portal_en", translations_dir))):
        app.installTranslator(translator)
    
    window = PortalWindow()
    window.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
