import subprocess
from venv import logger
from PyQt5.QtWidgets import QMenu
from PyQt5.QtCore import Qt
from core.models import BaseLesson
from core.config import PortalConfig
from portal.tr import tr

class UnitContextMenu(QMenu):
    def __init__(self, unit: BaseLesson, parent=None):
        super().__init__(parent)
        self.unit = unit
        self.config = PortalConfig.load()
        self.setup_menu()
        
    def setup_menu(self):
        editor_action = self.addAction(tr("Open in Editor"))
        editor_action.triggered.connect(self.open_in_editor)
        
        folder_action = self.addAction(tr("Open Folder"))
        folder_action.triggered.connect(self.open_folder)
        
    def open_in_editor(self):
        command = self.config.liascript_editor_open_command.replace("%f", str(self.unit.relative_markdown_path))
        subprocess.Popen(command, shell=True)
        
    def open_folder(self):
        folder_path = self.unit.markdown_path.parent
        if folder_path.exists():
            subprocess.Popen(['xdg-open', str(folder_path)])
