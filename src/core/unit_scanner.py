import os
from pathlib import Path
from typing import List, Optional
import logging
from fuzzywuzzy import fuzz
from core.models import Course, LessonMetadata, SimpleLesson, BaseLesson
from core.config import PortalConfig
from core.env_helper import EnvHelper

logger = logging.getLogger(__name__)

class UnitScanner:
    def __init__(self):
        self.config = PortalConfig.load()
        self.courses: List[Course] = []
        self._scan_courses()
    
    def _get_scan_paths(self) -> List[Path]:
        """Get paths to scan based on environment"""
        paths = []
        if EnvHelper.is_development():
            paths.append(Path("./OER-materials"))
        else:
            home = Path.home()
            paths.append(home / ".local/share/learning-portal/courses")
        return paths

    def _scan_courses(self) -> None:
        """Scan for courses in configured paths"""
        for base_path in self._get_scan_paths():
            if not base_path.exists():
                continue
                
            logger.info(f"Scanning courses in {base_path}")
            
            # Iterate through course collections
            for collection_dir in base_path.iterdir():
                if not collection_dir.is_dir():
                    continue
                    
                collection_name = collection_dir.name
                if collection_name in ['examples', 'draft', 'private', 'unpublished']:
                    # Handle special collections
                    self._scan_collection(collection_dir, collection_name)
                else:
                    # Regular course collection
                    self._scan_collection(collection_dir, collection_name)

    def _scan_collection(self, collection_path: Path, collection_name: str) -> None:
        """Scan a course collection directory"""
        for course_dir in collection_path.iterdir():
            if not course_dir.is_dir():
                continue

            course = self._load_course(course_dir, collection_name)
            if course:
                self.courses.append(course)

    def _load_course(self, course_dir: Path, collection_name: str) -> Optional[Course]:
        """Load a course from a directory"""
        try:
            course_yml = course_dir / "course.yml"
            if course_yml.exists():
                course = Course.from_yaml_file(course_yml)
            else:
                # Create minimal course from directory name
                course = Course(
                    title=course_dir.name,
                    collection_name=collection_name
                )
            
            course.course_path = course_dir
            course.lessons = self._scan_lessons(course_dir)
            return course
            
        except Exception as e:
            logger.error(f"Error loading course from {course_dir}: {e}")
            return None

    def _scan_lessons(self, course_dir: Path) -> List[BaseLesson]:
        """Scan for lessons in a course directory"""
        lessons = []
        
        for lesson_dir in course_dir.iterdir():
            if not lesson_dir.is_dir():
                continue

            lesson = self._load_lesson(lesson_dir)
            if lesson:
                lessons.append(lesson)
                
        return sorted(lessons, key=lambda l: l.lesson_path.name)

    def _load_lesson(self, lesson_dir: Path) -> Optional[BaseLesson]:
        """Load a lesson from a directory"""
        try:
            lesson_yml = lesson_dir / "lesson.yml"
            content_md = lesson_dir / "content.md"
            
            if not content_md.exists():
                return None
                
            if lesson_yml.exists():
                lesson = LessonMetadata.from_yaml_file(lesson_yml)
                lesson.content_path = content_md
                lesson.lesson_path = lesson_dir
                return lesson
            else:
                # Create simple lesson from markdown file
                return SimpleLesson(
                    title=lesson_dir.name,
                    content_path=content_md,
                    lesson_path=lesson_dir
                )
                
        except Exception as e:
            logger.error(f"Error loading lesson from {lesson_dir}: {e}")
            return None
    
    def search(self, query: str, min_score: int = 60) -> List[BaseLesson]:
        """
        Search lessons by title using fuzzy matching
        Args:
            query: Search string
            min_score: Minimum fuzzy match score (0-100)
        Returns:
            List of matching Lesson objects
        """
        results = []
        for course in self.courses:
            for lesson in course.lessons:
                score = fuzz.partial_ratio(query.lower(), lesson.title.lower())
                if score >= min_score:
                    results.append(lesson)
        return sorted(results, key=lambda x: fuzz.partial_ratio(query.lower(), x.title.lower()), reverse=True)
    
    def list_all_lessons(self) -> List[BaseLesson]:
        """Return all lessons from all courses"""
        return [lesson for course in self.courses for lesson in course.lessons]
    
    def list_all_courses(self) -> List[Course]:
        """Return all courses"""
        return self.courses
    
    def filter_by_subject(self, subject: str) -> List[BaseLesson]:
        """Filter lessons by subject (only works for LessonMetadata)"""
        results = []
        for lesson in self.list_all_lessons():
            if isinstance(lesson, LessonMetadata) and subject in lesson.subjects:
                results.append(lesson)
        return results
    
    def filter_by_grade(self, grade: int) -> List[BaseLesson]:
        """Filter lessons by minimum grade level (only works for LessonMetadata)"""
        results = []
        for lesson in self.list_all_lessons():
            if isinstance(lesson, LessonMetadata) and lesson.min_grade <= grade:
                results.append(lesson)
        return results
