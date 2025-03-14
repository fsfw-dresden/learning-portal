import os
from pathlib import Path
from typing import List, Optional
import logging
from fuzzywuzzy import fuzz
from core.models import Course, CourseMetadata, Lesson, LessonMetadata, BaseLesson, CourseCollection
from core.config import PortalConfig
from core.env_helper import EnvHelper

logger = logging.getLogger(__name__)

class UnitScanner:
    def __init__(self):
        self.config = PortalConfig.load()
        self.courses: List[Course] = []
        self.collections: List[CourseCollection] = []
        self._scan_courses()
    
    def _scan_courses(self) -> None:
        """Scan for courses in configured paths"""
        base_path = self.config.get_scan_path()
        if not base_path.exists():
            logger.error(f"Scan path {base_path} does not exist")
            return
            
        # Iterate through course collections
        for collection_dir in base_path.iterdir():
            if not collection_dir.is_dir():
                continue
                
            collection_name = collection_dir.name
            self._scan_collection(collection_dir, collection_name)

    def _scan_collection(self, collection_path: Path, collection_name: str) -> None:
        """Scan a course collection directory"""
        writable = True # if collection_name in ['drafts', 'private', 'unpublished'] else False
        collection = CourseCollection(
            title=collection_name,
            unique_collection_name=collection_name,
            collection_path=collection_path,
            writable=writable
        )
        self.collections.append(collection)
        
        for course_dir in collection_path.iterdir():
            if not course_dir.is_dir():
                continue
                
            course = self._load_course(course_dir, collection_name)
            if course:
                self.courses.append(course)
    
    def _load_course(self, course_dir: Path, collection_name: str) -> Optional[Course]:
        """Load a course from a directory"""
        course_yml = course_dir / "course.yml"
        if course_yml.exists():
            try:
                # Load CourseMetadata from YAML
                course_metadata = CourseMetadata.from_yaml_file(course_yml)
                
                # Create Course with metadata
                course = Course(
                    title=course_metadata.title,
                    collection_name=collection_name,
                    course_path=course_dir,
                    metadata=course_metadata
                )
            except Exception as e:
                logger.error(f"Error loading course from {course_yml}: {e}")
                # Create minimal course from directory name
                course = Course(
                    title=course_dir.name,
                    collection_name=collection_name,
                    course_path=course_dir
                )
        else:
            # Create minimal course from directory name
            course = Course(
                title=course_dir.name,
                collection_name=collection_name,
                course_path=course_dir
            )
        
        course.lessons = self._scan_lessons(course_dir)
        return course
    
    def _scan_lessons(self, course_dir: Path) -> List[BaseLesson]:
        """Scan for lessons in a course directory"""
        lessons = []
        
        # Check for lessons directory
        lessons_dir = course_dir
        if lessons_dir.exists() and lessons_dir.is_dir():
            # Scan lessons directory
            for lesson_dir in lessons_dir.iterdir():
                if not lesson_dir.is_dir():
                    continue
                    
                lesson = self._load_lesson(lesson_dir)
                if lesson:
                    lessons.append(lesson)
        else:
            # Check for markdown files directly in course directory
            for md_file in course_dir.glob("*.md"):
                if md_file.is_file():
                    # Create lesson from markdown file
                    lesson = Lesson(
                        title=md_file.stem,
                        content_path=md_file.as_posix(),
                        lesson_path=course_dir.as_posix()
                    )
                    lessons.append(lesson)
        
        return lessons
    
    def _find_content_file(self, lesson_dir: Path) -> Optional[Path]:
        """Find the main content file in a lesson directory"""
        # Look for README.md first
        readme = lesson_dir / "README.md"
        if readme.exists():
            return readme
            
        # Then look for any markdown file
        md_files = list(lesson_dir.glob("*.md"))
        if md_files:
            return md_files[0]
            
        return None
    
    def _load_lesson(self, lesson_dir: Path) -> Optional[BaseLesson]:
        """Load a lesson from a directory"""
        try:
            content_path = self._find_content_file(lesson_dir)
            if not content_path:
                return None

            lesson_yml = lesson_dir / "lesson.yml"
            if not lesson_yml.exists():
                lesson_yml = lesson_dir / "metadata.yml"
                
            if lesson_yml.exists():
                logger.info(f"Loading lesson metadata from {lesson_yml}")
                try:
                    # Load LessonMetadata from YAML
                    lesson_metadata = LessonMetadata.from_yaml_file(lesson_yml)
                    
                    # Determine content path
                    if not lesson_metadata.markdown_file:
                        content_path = self._find_content_file(lesson_dir)
                        if not content_path:
                            return None
                        content_path_str = content_path.as_posix()
                    else:
                        content_path_str = (lesson_dir / lesson_metadata.markdown_file).as_posix()
                    
                    # Create Lesson with metadata
                    lesson = Lesson(
                        title=lesson_metadata.title,
                        content_path=content_path_str,
                        lesson_path=lesson_dir.as_posix(),
                        metadata=lesson_metadata
                    )
                    
                    if lesson.validate():
                        return lesson
                    else:
                        logger.error(f"Lesson is invalid: {lesson}")
                        return None
                except Exception as e:
                    logger.error(f"Error parsing lesson metadata from {lesson_yml}: {e}")
                    return None
            else:
                # Create lesson from markdown file
                logger.info(f"Creating simple lesson from {content_path}")
                dir_path = Path(lesson_dir)
                return Lesson(
                    title=dir_path.parent.name + " - " + dir_path.name,
                    content_path=content_path.as_posix(),
                    lesson_path=lesson_dir.as_posix()
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

    def list_all_collections(self) -> List[CourseCollection]:
        """Return all collections"""
        return self.collections

    def filter_course_by_collection(self, collection_name: str) -> List[Course]:
        """Filter courses by collection name"""
        return [course for course in self.courses if course.collection_name == collection_name]
    
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
