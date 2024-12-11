import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTranslator, QLocale, Qt
from core.models import UnitMetadata
from tutor.tutor import TutorView
from tutor.tutor_proxy import TutorViewProxy

def main():
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    app = QApplication(sys.argv)

    # Initialize translation
    translator = QTranslator()
    locale = QLocale()
    try:
        import pkg_resources
        translations_dir = pkg_resources.resource_filename('tutor', 'translations')
    except (ImportError, pkg_resources.DistributionNotFound):
        translations_dir = os.path.join(os.path.dirname(__file__), "translations")
    
    # Try loading translations in order of preference
    if (translator.load(locale, "tutor", "_", translations_dir) or
        translator.load(QLocale(locale.language()), "tutor", "_", translations_dir) or
        (locale.language() != QLocale.English and translator.load("tutor_en", translations_dir))):
        app.installTranslator(translator)
    
    if len(sys.argv) > 1:
        # Load unit from provided directory
        unit_dir = Path(sys.argv[1])
        if not unit_dir.exists():
            print(f"Error: Directory {unit_dir} does not exist")
            sys.exit(1)
            
        metadata_file = unit_dir / "metadata.yml"
        if not metadata_file.exists():
            print(f"Error: No metadata.yml found in {unit_dir}")
            sys.exit(1)
            
        try:
            unit = UnitMetadata.from_yaml_file(metadata_file)
            unit.unit_path = unit_dir
            TutorViewProxy.get_instance().open_tutor(unit)
            return app.exec_()
        except Exception as e:
            print(f"Error loading unit: {e}")
            sys.exit(1)
    else:
        print("Usage: python -m tutor.main <unit_directory>")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())
