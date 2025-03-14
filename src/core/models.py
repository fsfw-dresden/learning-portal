from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Any
from dataclass_wizard import YAMLWizard
from enum import Enum
import os
import logging
from core.config import PortalConfig
from core.env_helper import EnvHelper

logger = logging.getLogger(__name__)

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
class LessonMetadata(YAMLWizard):
    """Serializable metadata for lessons"""
    title: str
    tags: List[str] = field(default_factory=list)
    min_grade: int = 0
    skill_level: int = 1
    subjects: List[str] = field(default_factory=list)
    skill_level_per_subject: Dict[str, int] = field(default_factory=dict)
    markdown_file: Optional[str] = None
    preview_image: Optional[str] = None
    screen_hint: Optional[ScreenHint] = None
    program_launch_info: Optional[ProgramLaunchInfo] = None

@dataclass
class BaseLesson:
    """Base class for all lessons"""
    title: str
    content_path: Optional[str] = None
    lesson_path: Optional[str] = None
    metadata: Optional[LessonMetadata] = None
    
    @property
    def markdown_path(self) -> Optional[Path]:
        if not self.content_path:
            return None
        return Path(self.content_path)

    @property
    def relative_markdown_path(self) -> Optional[str]:
        if not self.content_path:
            return None
        config = PortalConfig.load()
        scan_path = config.get_scan_path()
        relative_path = Path(self.content_path).relative_to(scan_path)
        return relative_path.as_posix()
    
    @property
    def tutorial_url(self) -> Optional[str]:
        if not self.content_path:
            return None
        config = PortalConfig.load()
        liascript_url = f"{config.liascript_devserver}{config.liascript_html_path}?{config.liascript_devserver}/"
        return f"{liascript_url}{self.relative_markdown_path}"
    
    def validate(self) -> bool:
        if not self.content_path:
            return False
        if not self.lesson_path:
            return False
        return True
    
    @property
    def preview_path(self) -> Optional[Path]:
        if not self.metadata or not self.metadata.preview_image or not self.lesson_path:
            return None
        return Path(self.lesson_path) / self.metadata.preview_image
    
    def save(self) -> bool:
        """
        Save the lesson metadata to a lesson.yml file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.lesson_path or not self.metadata:
            logger.error("Cannot save lesson: lesson_path or metadata is not set")
            return False
            
        lesson_dir = Path(self.lesson_path)
        if not lesson_dir.exists():
            try:
                os.makedirs(lesson_dir, exist_ok=True)
                logger.info(f"Created lesson directory: {lesson_dir}")
            except Exception as e:
                logger.error(f"Failed to create lesson directory {lesson_dir}: {e}")
                return False
        
        lesson_yml_path = lesson_dir / "lesson.yml"
        
        try:
            # Save metadata
            yaml_content = self.metadata.to_yaml()
            
            with open(lesson_yml_path, 'w') as f:
                f.write(yaml_content)
                
            logger.info(f"Saved lesson metadata to {lesson_yml_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save lesson metadata to {lesson_yml_path}: {e}")
            return False

@dataclass 
class SimpleLesson(BaseLesson):
    """Simple lesson with just markdown content and no metadata"""
    pass

@dataclass
class Lesson(BaseLesson):
    """Full lesson with metadata"""
    def __init__(self, title: str, content_path: Optional[str] = None, 
                 lesson_path: Optional[str] = None, metadata: Optional[LessonMetadata] = None):
        super().__init__(title, content_path, lesson_path, metadata)
        
        # If no metadata was provided, create default metadata
        if not self.metadata:
            self.metadata = LessonMetadata(title=title)

@dataclass
class CourseMetadata(YAMLWizard):
    """Serializable metadata for courses"""
    title: str
    collection_name: str
    description: Optional[str] = None
    preview_image: Optional[str] = None

@dataclass
class Course:
    """Course containing multiple lessons"""
    title: str
    collection_name: str  # e.g. org_gitlab_user_repo
    course_path: Optional[Path] = None
    lessons: List[BaseLesson] = field(default_factory=list)
    metadata: Optional[CourseMetadata] = None
    
    def __post_init__(self):
        # If no metadata was provided, create default metadata
        if not self.metadata:
            self.metadata = CourseMetadata(
                title=self.title,
                collection_name=self.collection_name
            )

    @property
    def description(self) -> Optional[str]:
        """Get description from metadata"""
        return self.metadata.description if self.metadata else None
    
    @description.setter
    def description(self, value: Optional[str]):
        """Set description in metadata"""
        if self.metadata:
            self.metadata.description = value
    
    @property
    def preview_image(self) -> Optional[str]:
        """Get preview_image from metadata"""
        return self.metadata.preview_image if self.metadata else None
    
    @preview_image.setter
    def preview_image(self, value: Optional[str]):
        """Set preview_image in metadata"""
        if self.metadata:
            self.metadata.preview_image = value

    @property
    def preview_path(self) -> Optional[Path]:
        if not self.preview_image or not self.course_path:
            return None
        return Path(self.course_path) / self.preview_image

    def get_relative_path(self) -> Optional[Path]:
        if not self.course_path:
            return None
        config = PortalConfig.load()
        if Path(self.course_path).is_absolute():
            return Path(self.course_path).relative_to(config.unit_root_path)
        return self.course_path
    
    def save(self) -> bool:
        """
        Save the course metadata to a course.yml file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.course_path or not self.metadata:
            logger.error("Cannot save course: course_path or metadata is not set")
            return False
            
        course_dir = Path(self.course_path)
        if not course_dir.exists():
            try:
                os.makedirs(course_dir, exist_ok=True)
                logger.info(f"Created course directory: {course_dir}")
            except Exception as e:
                logger.error(f"Failed to create course directory {course_dir}: {e}")
                return False
        
        course_yml_path = course_dir / "course.yml"
        
        try:
            # Update metadata with current title and collection_name
            self.metadata.title = self.title
            self.metadata.collection_name = self.collection_name
            
            # Save metadata
            yaml_content = self.metadata.to_yaml()
            
            with open(course_yml_path, 'w') as f:
                f.write(yaml_content)
                
            logger.info(f"Saved course metadata to {course_yml_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save course metadata to {course_yml_path}: {e}")
            return False

# Keeping UnitMetadata for backwards compatibility
UnitMetadata = LessonMetadata

@dataclass
class CourseCollection:
    """Collection of courses"""
    title: str
    unique_collection_name: str
    collection_path: Path
    collection_remote_url: Optional[str] = None
    writable: bool = False