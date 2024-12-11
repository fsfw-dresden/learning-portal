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
        
    def open_in_editor(self):
        url = f"{self.config.liascript_editor_url}{self.config.liascript_editor_proxy_static_url}{self.unit.relative_markdown_path}"
        logger.info(f"Opening {url} in editor")
        logger.info(f"Command: {self.config.liascript_editor_open_command}{url}")
        command = f"{self.config.liascript_editor_open_command}{url}"
        subprocess.Popen(command, shell=True)
