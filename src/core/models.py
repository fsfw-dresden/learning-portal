from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
from dataclass_wizard import YAMLWizard
from enum import Enum
from core.config import PortalConfig

class DockPosition(str, Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left" 
    RIGHT = "right"

class ViewMode(str, Enum):
    DOCKED = "docked"
    FREE = "free"

@dataclass
class ScreenHint:
    position: Optional[DockPosition] = None
    mode: ViewMode = ViewMode.DOCKED
    preferred_width: Optional[int] = None
    preferred_height: Optional[int] = None 
    preferred_aspect: Optional[float] = None

@dataclass
class ProgramLaunchInfo:
    bin_name: str
    path: Optional[str] = None
    args: Optional[List[str]] = None

@dataclass
class UnitMetadata(YAMLWizard):
    title: str
    tags: List[str]
    min_grade: int
    skill_level: int
    subjects: List[str]
    skill_level_per_subject: Dict[str, int]
    markdown_file: str
    preview_image: str
    screen_hint: Optional[ScreenHint] = None
    unit_url: str = None
    html_path: str = None
    unit_path: str = None
    program_launch_info: Optional[ProgramLaunchInfo] = None

    @property
    def tutorial_url(self) -> Optional[str]:
        config = PortalConfig.load()
        liascript_url = f"{config.liascript_devserver}{config.liascript_html_path}?{config.liascript_devserver}/"
        unit_path = self.get_relative_unit_path()
        return f"{liascript_url}{unit_path / self.markdown_file}"

    def get_relative_unit_path(self) -> Optional[Path]:
        config = PortalConfig.load()
        unit_path = Path(self.unit_path)
        if unit_path.is_absolute():
            return unit_path.relative_to(config.unit_root_path)
        return unit_path

    @property
    def markdown_path(self) -> Optional[Path]:
        if self.unit_path is None:
            return None
        return Path(self.unit_path) / self.markdown_file
    
    @property
    def preview_path(self) -> Optional[Path]:
        if self.unit_path is None:
            return None
        return Path(self.unit_path) / self.preview_image
