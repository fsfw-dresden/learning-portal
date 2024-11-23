import logging
from PyQt5.QtWidgets import (QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, 
                            QLabel, QRadioButton, QButtonGroup, QGridLayout,
                            QWidget, QPushButton, QApplication)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from vision_assistant.tutor import TutorView
from core.preferences import Preferences, SkillLevelPreferences

class WelcomePage(QWizardPage):
    def __init__(self):
        super().__init__()
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Load preferences
        self.preferences = Preferences.load()
        self.logger.info(f"Loaded preferences from: {Preferences._get_config_path()}")
        
        layout = QVBoxLayout()
        
        welcome_label = QLabel(self.tr("Welcome!"))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        desc_label = QLabel(self.tr("to your personal learning portal on the Schulstick. "
                                   "The Schulstick will help you learn many programs that "
                                   "can help you in everyday life."))
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("font-size: 18px;")
        
        layout.addStretch()
        layout.addWidget(welcome_label)
        layout.addWidget(desc_label)
        layout.addStretch()
        
        self.setLayout(layout)

class GradePage(QWizardPage):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        question_label = QLabel(self.tr("To customize learning for you, please answer the following questions:"))
        question_label.setWordWrap(True)
        
        grade_label = QLabel(self.tr("What grade are you in?"))
        grade_label.setStyleSheet("font-weight: bold;")
        
        self.grade_group = QButtonGroup()
        grades = ["4", "5", "6", "7", "8+"]
        
        for i, grade in enumerate(grades):
            radio = QRadioButton(self.tr("%sth grade") % grade)
            self.grade_group.addButton(radio, i)
            layout.addWidget(radio)
            
        layout.insertWidget(0, question_label)
        layout.insertWidget(1, grade_label)
        
        self.registerField("grade*", self.grade_group.buttons()[0])
        self.setLayout(layout)

class SkillLevelPage(QWizardPage):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        question_label = QLabel(self.tr("How do you rate yourself in the following areas?"))
        question_label.setWordWrap(True)
        
        grid = QGridLayout()
        subjects = [
            self.tr("German"),
            self.tr("Foreign Language"),
            self.tr("Mathematics"),
            self.tr("Computer Science"),
            self.tr("Natural Science")
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
    
    def update_stars(self, subject, rating):
        buttons = self.ratings[subject].buttons()
        for i, btn in enumerate(buttons):
            btn.setIcon(QIcon.fromTheme("starred-symbolic" if i < rating else "non-starred-symbolic"))

class CompletionPage(QWizardPage):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        done_label = QLabel(self.tr("Done!"))
        done_label.setAlignment(Qt.AlignCenter)
        done_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        
        message_label = QLabel(self.tr("The recommendations will now be tailored to you!"))
        message_label.setWordWrap(True)
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 18px;")
        
        layout.addStretch()
        layout.addWidget(done_label)
        layout.addWidget(message_label)
        layout.addStretch()
        
        self.setLayout(layout)

class WelcomeWizard(QWizard):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Schulstick")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add pages
        self.addPage(WelcomePage())
        self.addPage(GradePage())
        self.addPage(SkillLevelPage())
        self.addPage(CompletionPage())
        
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
        # Save preferences
        self.preferences.skill.grade = self.field("grade")
        self.preferences.save()
        self.logger.info(f"Saved preferences to: {Preferences._get_config_path()}")
        
        # Start tutor view
        self.tutor = TutorView()
        self.tutor.show()
