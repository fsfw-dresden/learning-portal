import logging
from abc import ABCMeta, abstractmethod
from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, 
                            QLabel, QRadioButton, QButtonGroup, QGridLayout,
                            QWidget, QPushButton, QApplication)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from vision_assistant.tutor import TutorView
from core.preferences import Preferences, SkillLevelPreferences


# Translation context for all wizard pages
TRANSLATION_CONTEXT = "WelcomeWizard"

def tr(text: str, *args) -> str:
    """Helper function for translations with variable substitution"""
    translated = QApplication.translate(TRANSLATION_CONTEXT, text)
    if args:
        return translated % args
    return translated

class WelcomeWizardPageMeta(type(QWizardPage), ABCMeta):
    pass

class WelcomeWizardPage(QWizardPage, metaclass=WelcomeWizardPageMeta):
    """Abstract base class for all welcome wizard pages"""
    def __init__(self, preferences: Preferences):
        super().__init__()
        self.preferences = preferences
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)
        
    @abstractmethod
    def setup_ui(self):
        """Setup the UI elements for this page"""
        pass
class WelcomePage(WelcomeWizardPage):
    def __init__(self, preferences: Preferences):
        super().__init__(preferences)
        self.setup_ui()
        
    def setup_ui(self):
        welcome_label = QLabel(tr("Welcome!"))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        desc_label = QLabel(tr("to your personal learning portal on the Schulstick. "
                              "The Schulstick will help you learn many programs that "
                              "can help you in everyday life."))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 18px;")
        
        self.main_layout.addStretch()
        self.main_layout.addWidget(welcome_label)
        self.main_layout.addWidget(desc_label)
        self.main_layout.addStretch()

class GradePage(WelcomeWizardPage):
    def __init__(self, preferences: Preferences):
        super().__init__(preferences)
        self.grade_group = QButtonGroup()
        self.setup_ui()
        
    def setup_ui(self):
        question_label = QLabel(tr("To customize learning for you, please answer the following questions:"))
        question_label.setWordWrap(True)
        
        grade_label = QLabel(tr("What grade are you in?"))
        grade_label.setStyleSheet("font-weight: bold;")
        
        grades = ["4", "5", "6", "7", "8+"]
        
        # Create radio buttons for grades
        grade_layout = QVBoxLayout()
        for i, grade in enumerate(grades):
            radio = QRadioButton(tr("%sth grade", grade))
            self.grade_group.addButton(radio, i)
            grade_layout.addWidget(radio)
            # Register field for each grade button
            self.registerField(f"grade_{grade}", radio)
            
        self.main_layout.addWidget(question_label)
        self.main_layout.addWidget(grade_label)
        self.main_layout.addLayout(grade_layout)
        
        # Set initial state from preferences
        if self.preferences.skill.grade:
            for btn in self.grade_group.buttons():
                if btn.text() == tr("%sth grade", str(self.preferences.skill.grade)):
                    btn.setChecked(True)
                    break

class SkillLevelPage(WelcomeWizardPage):
    def __init__(self, preferences: Preferences):
        super().__init__(preferences)
        self.ratings = {}
        self.setup_ui()
        
    def setup_ui(self):
        
        question_label = QLabel(tr("How do you rate yourself in the following areas?"))
        question_label.setWordWrap(True)
        
        grid = QGridLayout()
        subjects = [
            tr("German"),
            tr("Foreign Language"),
            tr("Mathematics"),
            tr("Computer Science"),
            tr("Natural Science")
        ]
        
        self.ratings = {}
        for i, subject in enumerate(subjects):
            label = QLabel(subject)
            stars_widget = QWidget()
            stars_layout = QHBoxLayout(stars_widget)
            stars_layout.setSpacing(5)
            
            star_group = QButtonGroup()
            self.ratings[subject] = star_group
            
            for j in range(5):
                star_btn = QPushButton()
                star_btn.setCheckable(True)
                star_btn.setFixedSize(QSize(24, 24))
                star_btn.setIcon(QIcon.fromTheme("non-starred-symbolic"))
                star_btn.clicked.connect(lambda checked, s=subject, rating=j+1:
                                       self.update_stars(s, rating))
                star_group.addButton(star_btn, j)
                stars_layout.addWidget(star_btn)
            
            grid.addWidget(label, i, 0)
            grid.addWidget(stars_widget, i, 1)
        
        layout.addWidget(question_label)
        layout.addLayout(grid)
        self.setLayout(layout)
    
    def initializePage(self):
        # Load initial ratings from preferences
        subject_map = {
            tr("German"): self.preferences.skill.german,
            tr("Foreign Language"): self.preferences.skill.foreign_language,
            tr("Mathematics"): self.preferences.skill.mathematics,
            tr("Computer Science"): self.preferences.skill.computer_science,
            tr("Natural Science"): self.preferences.skill.natural_science
        }
        
        for subject, rating in subject_map.items():
            if rating:
                self.update_stars(subject, rating)

    def update_stars(self, subject, rating):
        buttons = self.ratings[subject].buttons()
        for i, btn in enumerate(buttons):
            btn.setIcon(QIcon.fromTheme("starred-symbolic" if i < rating else "non-starred-symbolic"))
        
        # Store the rating in a field
        self.registerField(f"rating_{subject}", buttons[rating-1])

class CompletionPage(WelcomeWizardPage):
    def __init__(self, preferences: Preferences):
        super().__init__(preferences)
        self.setup_ui()
        
    def setup_ui(self):
        done_label = QLabel(tr("Done!"))
        done_label.setAlignment(Qt.AlignCenter)
        done_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        message_label = QLabel(tr("The recommendations will now be tailored to you!"))
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 18px;")
        
        self.main_layout.addStretch()
        self.main_layout.addWidget(done_label)
        self.main_layout.addWidget(message_label)
        self.main_layout.addStretch()

class WelcomeWizard(QWizard):
    def __init__(self):
        super().__init__()
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load preferences
        self.preferences = Preferences.load()
        self.logger.info(f"Loaded preferences from: {Preferences._get_config_path()}")
        
        self.setWindowTitle("Schulstick")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add pages
        self.addPage(WelcomePage(self.preferences))
        self.addPage(GradePage(self.preferences))
        self.addPage(SkillLevelPage(self.preferences))
        self.addPage(CompletionPage(self.preferences))
        
        # Style navigation buttons
        self.setButtonText(QWizard.NextButton, "")
        self.setButtonText(QWizard.BackButton, "")
        self.button(QWizard.NextButton).setIcon(QIcon.fromTheme("go-next"))
        self.button(QWizard.BackButton).setIcon(QIcon.fromTheme("go-previous"))
        
        # Center on screen
        self.resize(600, 400)
        screen = QApplication.primaryScreen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )
        
        self.finished.connect(self.on_finish)
    
    def on_finish(self):
        # Get selected grade
        for grade in ["4", "5", "6", "7", "8+"]:
            if self.field(f"grade_{grade}"):
                self.preferences.skill.grade = int(grade.rstrip('+'))
                break
        
        # Get ratings
        subject_map = {
            tr("German"): "german",
            tr("Foreign Language"): "foreign_language",
            tr("Mathematics"): "mathematics",
            tr("Computer Science"): "computer_science",
            tr("Natural Science"): "natural_science"
        }
        
        for display_name, pref_name in subject_map.items():
            for i, btn in enumerate(self.ratings[display_name].buttons()):
                if btn.isChecked():
                    setattr(self.preferences.skill, pref_name, i + 1)
                    break
        
        # Save preferences
        self.preferences.save()
        self.logger.info(f"Saved preferences to: {Preferences._get_config_path()}")
        
        # Start tutor view
        self.tutor = TutorView()
        self.tutor.show()
