import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale
from welcome.wizard import WelcomeWizard

def main():
    app = QApplication(sys.argv)
    
    # Setup translation
    translator = QTranslator()
    translator.load(QLocale(), "de", "", ":/translations")
    app.installTranslator(translator)
    
    wizard = WelcomeWizard()
    wizard.show()
    return app.exec_()

if __name__ == "__main__":
    sys.exit(main())
