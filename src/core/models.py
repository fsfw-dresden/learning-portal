from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from dataclass_wizard import YAMLWizard
from enum import Enum
from core.config import PortalConfig
from core.env_helper import EnvHelper

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
class BaseLesson:
    """Base class for all lessons"""
    title: str
    content_path: Optional[Path] = None
    lesson_path: Optional[Path] = None
    
    @property
    def markdown_path(self) -> Path:
        return self.content_path
    
    def validate(self):
        if not self.content_path:
            raise ValueError("content_path is required")
        if not self.lesson_path:
            raise ValueError("lesson_path is required")

@dataclass
class LessonMetadata(BaseLesson, YAMLWizard):
    """Lesson with metadata from lesson.yml"""
    tags: List[str] = field(default_factory=list)
    min_grade: int = 0
    skill_level: int = 1
    subjects: List[str] = field(default_factory=list)
    skill_level_per_subject: Dict[str, int] = field(default_factory=dict)
    markdown_file: Optional[str] = None
    preview_image: Optional[str] = None
    screen_hint: Optional[ScreenHint] = None
    program_launch_info: Optional[ProgramLaunchInfo] = None

    @property
    def preview_path(self) -> Optional[Path]:
        if not self.preview_image:
            return None
        return self.lesson_path / self.preview_image

@dataclass 
class SimpleLesson(BaseLesson):
    """Simple lesson with just markdown content"""
    pass

@dataclass
class Course(YAMLWizard):
    """Course containing multiple lessons"""
    title: str
    collection_name: str  # e.g. org_gitlab_user_repo
    description: Optional[str] = None
    preview_image: Optional[str] = None
    course_path: Optional[Path] = None
    lessons: List[BaseLesson] = field(default_factory=list)

    @property
    def preview_path(self) -> Optional[Path]:
        if not self.preview_image or not self.course_path:
            return None
        return self.course_path / self.preview_image

    def get_relative_path(self) -> Optional[Path]:
        if not self.course_path:
            return None
        config = PortalConfig.load()
        if self.course_path.is_absolute():
            return self.course_path.relative_to(config.unit_root_path)
        return self.course_path

# Keeping UnitMetadata for backwards compatibility
UnitMetadata = LessonMetadata
