"""
Demo application for the ListOfThingsWidget.
"""

import sys
from dataclasses import dataclass, field
from typing import List, Optional
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QWidget, QPushButton, QLabel

from .list_of_things_widget import ListOfThingsWidget
from .form_generator import DataclassFormGenerator, FormField

@dataclass
class Address:
    street: str
    city: str
    zip_code: str
    
    def __str__(self):
        return f"{self.street}, {self.city} {self.zip_code}"

@dataclass
class Person:
    name: str
    age: int = field(metadata=FormField.number(min_value=0, max_value=120, use_slider=True))
    rating: float = field(default=5.0, metadata=FormField.number(min_value=0.0, max_value=10.0, use_slider=True))
    email: Optional[str] = None
    internal_id: str = field(default="", metadata=FormField.hidden())
    
    def __str__(self):
        return f"{self.name} ({self.age}) - Rating: {self.rating}"

@dataclass
class Team:
    name: str
    members: List[Person] = field(default_factory=list)
    address: Optional[Address] = None
    
    def __str__(self):
        return f"{self.name} - {len(self.members)} members"

class DemoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("List of Things Demo")
        self.resize(800, 600)
        
        # Create main layout
        layout = QVBoxLayout(self)
        
        # Add title
        title = QLabel("List of Things Demo")
        title.setStyleSheet("font-size: 18pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Create some sample data
        self.team = Team(
            name="Development Team",
            members=[
                Person(name="Alice Smith", age=32, email="alice@example.com"),
                Person(name="Bob Johnson", age=28, email="bob@example.com"),
                Person(name="Charlie Brown", age=35)
            ],
            address=Address(street="123 Tech St", city="San Francisco", zip_code="94107")
        )
        
        # Create a form for the team
        self.team_form = DataclassFormGenerator.create_form(Team, self)
        self.team_form.set_value(self.team)
        layout.addWidget(self.team_form)
        
        # Example of how to create a ListOfThingsWidget with a custom factory
        layout.addWidget(QLabel("Example with custom factory:"))
        self.custom_list = ListOfThingsWidget(
            Person, 
            self,
            custom_factory=lambda: Person(name="New Person", age=25)
        )
        layout.addWidget(self.custom_list)
        
        # Add a button to show the current value
        self.show_value_button = QPushButton("Show Current Value")
        self.show_value_button.clicked.connect(self.show_current_value)
        layout.addWidget(self.show_value_button)
        
        # Add a label to display the current value
        self.value_label = QLabel()
        self.value_label.setWordWrap(True)
        layout.addWidget(self.value_label)
    
    def show_current_value(self):
        """Show the current value of the form."""
        try:
            value = self.team_form.get_value()
            self.value_label.setText(f"Team: {value.name}\n\nMembers:")
            
            for i, member in enumerate(value.members):
                self.value_label.setText(
                    self.value_label.text() + 
                    f"\n{i+1}. {member.name}, {member.age}" + 
                    (f", {member.email}" if member.email else "")
                )
            
            if value.address:
                self.value_label.setText(
                    self.value_label.text() + 
                    f"\n\nAddress: {value.address.street}, {value.address.city} {value.address.zip_code}"
                )
        except Exception as e:
            self.value_label.setText(f"Error: {str(e)}")

def main():
    app = QApplication(sys.argv)
    window = DemoApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
