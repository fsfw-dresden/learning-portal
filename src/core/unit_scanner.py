from pathlib import Path
from typing import List
from venv import logger
from fuzzywuzzy import fuzz
from core.models import UnitMetadata
from core.config import PortalConfig

class UnitScanner:
    def __init__(self):
        self.config = PortalConfig.load()
        self.units: List[UnitMetadata] = []
        self._scan_units()
    
    def _scan_units(self) -> None:
        """Recursively scan for metadata.yml files in all configured paths"""
        seen_titles = set()
        logger.info(f"Scanning units in {self.config.unit_paths}")
        
        for base_path in self.config.unit_paths:
            path = Path(base_path)
            if not path.exists():
                continue
                
            for metadata_file in path.rglob("metadata.yml"):
                try:
                    unit = UnitMetadata.from_yaml_file(metadata_file)
                    if unit.title not in seen_titles:
                        unit.unit_path = metadata_file.parent
                        self.units.append(unit)
                        seen_titles.add(unit.title)
                except Exception as e:
                    print(f"Error parsing {metadata_file}: {e}")
    
    def search(self, query: str, min_score: int = 60) -> List[UnitMetadata]:
        """
        Search units by title using fuzzy matching
        Args:
            query: Search string
            min_score: Minimum fuzzy match score (0-100)
        Returns:
            List of matching UnitMetadata objects
        """
        results = []
        for unit in self.units:
            score = fuzz.partial_ratio(query.lower(), unit.title.lower())
            if score >= min_score:
                results.append(unit)
        return sorted(results, key=lambda x: fuzz.partial_ratio(query.lower(), x.title.lower()), reverse=True)
    
    def list_all(self) -> List[UnitMetadata]:
        """Return all units"""
        return self.units
    
    def filter_by_subject(self, subject: str) -> List[UnitMetadata]:
        """Filter units by subject"""
        return [unit for unit in self.units if subject in unit.subjects]
    
    def filter_by_grade(self, grade: int) -> List[UnitMetadata]:
        """Filter units by minimum grade level"""
        return [unit for unit in self.units if unit.min_grade <= grade]
