"""
Widget for editing a list of dataclass objects.
"""

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QHBoxLayout, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, 
    QDialog, QScrollArea, QMessageBox
)
from typing import List, Type, TypeVar, Optional, Callable
from dataclasses import is_dataclass

from .widget_interfaces import ListWidgetBase

T = TypeVar('T')

class ListOfThingsWidget(ListWidgetBase[T]):
    """
    A widget for editing a list of dataclass objects.
    
    This widget provides a list view with buttons to add, edit, and remove items.
    Each item in the list is displayed using its __str__ method.
    """
    
    def __init__(self, item_type: Type[T], parent=None, items: Optional[List[T]] = None,
                 custom_factory: Optional[Callable[[], T]] = None):
        """
        Initialize the list of things widget.
        
        Args:
            item_type: The dataclass type of items in the list
            parent: Parent widget
            items: Optional initial list of items
            custom_factory: Optional factory function to create new items
        """
        super().__init__(parent)
        
        if not is_dataclass(item_type):
            raise ValueError(f"{item_type.__name__} is not a dataclass")
        
        self.item_type = item_type
        self.custom_factory = custom_factory
        self.items: List[T] = []
        
        self._setup_ui()
        
        # Initialize with items if provided
        if items and hasattr(items, '__iter__'):
            self.set_items(items)
    
    def _setup_ui(self):
        """Set up the user interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create list widget
        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)
        
        # Add buttons for managing the list
        buttons_layout = QHBoxLayout()
        self.add_button = QPushButton("Add", self)
        self.edit_button = QPushButton("Edit", self)
        self.remove_button = QPushButton("Remove", self)
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.remove_button)
        layout.addLayout(buttons_layout)
        
        # Connect buttons
        self.add_button.clicked.connect(self._add_item)
        self.edit_button.clicked.connect(self._edit_selected_item)
        self.remove_button.clicked.connect(self._remove_selected_items)
        
        # Connect double-click to edit
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Connect list widget signals
        self.list_widget.model().rowsInserted.connect(self.valueChanged.emit)
        self.list_widget.model().rowsRemoved.connect(self.valueChanged.emit)
    
    def _add_item(self):
        """Add a new item to the list."""
        # Open a dialog to create a new item
        new_item = self._create_item_dialog()
        if new_item:
            # Add the item to our internal list
            self.items.append(new_item)
            
            # Add to the list widget
            item_text = str(new_item)
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, len(self.items) - 1)  # Store the index
            self.list_widget.addItem(list_item)
            
            # Emit value changed
            self.valueChanged.emit()
    
    def _on_item_double_clicked(self, item):
        """Handle double-click on an item."""
        self._edit_selected_item()
    
    def _edit_selected_item(self):
        """Edit the selected item in the list."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        
        # Get the first selected item
        list_item = selected_items[0]
        item_index = list_item.data(Qt.UserRole)
        
        if 0 <= item_index < len(self.items):
            item = self.items[item_index]
            
            # Open the edit dialog
            if self._edit_item_dialog(item):
                # Update the list widget text
                list_item.setText(str(item))
                
                # Emit value changed
                self.valueChanged.emit()
    
    def _create_item_dialog(self) -> Optional[T]:
        """
        Open a dialog to create a new item.
        
        Returns:
            Optional[T]: The created item or None if canceled
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Create {self.item_type.__name__}")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Import here to avoid circular imports
        from .form_generator import DataclassFormGenerator
        
        # Create a form for the item type
        form = DataclassFormGenerator.create_form(self.item_type, dialog)
        
        # If we have a custom factory, use it to initialize the form
        if self.custom_factory:
            try:
                initial_item = self.custom_factory()
                form.set_value(initial_item)
            except Exception:
                # If factory fails, continue with empty form
                pass
        
        # Add the form to a scroll area
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)
        layout.addWidget(scroll)
        
        # Add OK/Cancel buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        # Store references
        dialog.form = form
        dialog.new_item = None
        
        # Connect buttons
        ok_button.clicked.connect(lambda: self._handle_create_dialog_accept(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        # Show the dialog
        result = dialog.exec_()
        return dialog.new_item if result == QDialog.Accepted else None
    
    def _handle_create_dialog_accept(self, dialog):
        """Handle the accept action for the create dialog."""
        try:
            # Try to create a new item from the form
            dialog.new_item = dialog.form.get_value()
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Error creating item: {str(e)}")
    
    def _edit_item_dialog(self, item: T) -> bool:
        """
        Open a dialog to edit an item.
        
        Args:
            item: The item to edit
            
        Returns:
            bool: True if the item was edited, False if canceled
        """
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Edit {self.item_type.__name__}")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Import here to avoid circular imports
        from .form_generator import DataclassFormGenerator
        
        # Create a form for the item
        form = DataclassFormGenerator.create_form(self.item_type, dialog)
        form.set_value(item)
        
        # Add the form to a scroll area
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        scroll.setWidget(form)
        layout.addWidget(scroll)
        
        # Add OK/Cancel buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        # Store references
        dialog.form = form
        dialog.result_item = None
        
        # Connect buttons
        ok_button.clicked.connect(lambda: self._handle_dialog_accept(dialog, item))
        cancel_button.clicked.connect(dialog.reject)
        
        # Show the dialog
        result = dialog.exec_()
        return result == QDialog.Accepted
    
    def _handle_dialog_accept(self, dialog, original_item):
        """Handle the accept action for the edit dialog."""
        try:
            # Get the form value
            new_item = dialog.form.get_value()
            
            # Update the original item with the new values
            for field_name, field_value in new_item.__dict__.items():
                if not field_name.startswith('_'):
                    setattr(original_item, field_name, field_value)
            
            # Accept the dialog
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(dialog, "Error", f"Error updating item: {str(e)}")
    
    def _remove_selected_items(self):
        """Remove all selected items from the list."""
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            return
        
        # Remove items in reverse order to avoid index issues
        indices_to_remove = [item.data(Qt.UserRole) for item in selected_items]
        indices_to_remove.sort(reverse=True)
        
        for index in indices_to_remove:
            if 0 <= index < len(self.items):
                # Remove from our internal list
                self.items.pop(index)
        
        # Rebuild the list widget to update indices
        self._rebuild_list_widget()
        
        # Emit value changed
        self.valueChanged.emit()
    
    def _rebuild_list_widget(self):
        """Rebuild the list widget with current items."""
        self.list_widget.clear()
        
        for i, item in enumerate(self.items):
            item_text = str(item)
            list_item = QListWidgetItem(item_text)
            list_item.setData(Qt.UserRole, i)  # Store the index
            self.list_widget.addItem(list_item)
    
    def get_items(self) -> List[T]:
        """
        Get the current list of items.
        
        Returns:
            List of items
        """
        return self.items.copy()
    
    def set_items(self, items: List[T]):
        """
        Set the list of items.
        
        Args:
            items: List of items
        """
        if not items:
            self.items = []
        else:
            self.items = list(items)
        
        self._rebuild_list_widget()
        self.valueChanged.emit()
