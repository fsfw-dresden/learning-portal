"""
Form generator for dataclasses.
"""

import inspect
import typing
import dataclasses
from dataclasses import dataclass, field, fields, is_dataclass
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, get_type_hints, get_origin, get_args

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QScrollArea, QSpinBox,
    QTextEdit, QVBoxLayout, QWidget
)

T = TypeVar('T')

class DataclassForm(QWidget):
    """A form widget that is generated from a dataclass."""
    
    valueChanged = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QFormLayout(self)
        self._widgets = {}
        self._dataclass_instance = None
        self._dataclass_type = None
    
    def get_value(self):
        """Get the current value of the form as a dataclass instance."""
        if not self._dataclass_type:
            return None
        
        values = {}
        for field_name, widget in self._widgets.items():
            if isinstance(widget, QLineEdit):
                values[field_name] = widget.text()
            elif isinstance(widget, QTextEdit):
                values[field_name] = widget.toPlainText()
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                values[field_name] = widget.value()
            elif isinstance(widget, QCheckBox):
                values[field_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                values[field_name] = widget.currentText()
            elif isinstance(widget, QListWidget):
                items = []
                for i in range(widget.count()):
                    items.append(widget.item(i).text())
                values[field_name] = items
            elif isinstance(widget, DataclassForm):
                values[field_name] = widget.get_value()
            elif hasattr(widget, 'field_type') and is_dataclass(widget.field_type):
                # For nested dataclass containers, create a default instance with default values
                # This is a placeholder as we don't store the actual value
                field_cls = widget.field_type
                field_args = {}
                
                # Get required fields and provide default values
                for f in fields(field_cls):
                    if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING:
                        # Required field - provide a default value based on type
                        field_type = get_type_hints(field_cls).get(f.name)
                        if field_type == str:
                            field_args[f.name] = ""
                        elif field_type == int:
                            field_args[f.name] = 0
                        elif field_type == float:
                            field_args[f.name] = 0.0
                        elif field_type == bool:
                            field_args[f.name] = False
                        elif get_origin(field_type) is list:
                            field_args[f.name] = []
                        else:
                            field_args[f.name] = None
                
                values[field_name] = field_cls(**field_args)
        
        return self._dataclass_type(**values)
    
    def set_value(self, value):
        """Set the form values from a dataclass instance."""
        if not is_dataclass(value):
            raise ValueError("Value must be a dataclass instance")
        
        self._dataclass_instance = value
        self._dataclass_type = type(value)
        
        for field_name, field_value in inspect.getmembers(value):
            if field_name.startswith('_') or field_name not in self._widgets:
                continue
            
            widget = self._widgets[field_name]
            if isinstance(widget, QLineEdit):
                widget.setText(str(field_value))
            elif isinstance(widget, QTextEdit):
                widget.setPlainText(str(field_value))
            elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
                widget.setValue(field_value)
            elif isinstance(widget, QCheckBox):
                widget.setChecked(field_value)
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(field_value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif isinstance(widget, QListWidget):
                widget.clear()
                for item in field_value:
                    widget.addItem(str(item))
            elif isinstance(widget, DataclassForm):
                widget.set_value(field_value)
            elif hasattr(widget, 'field_type') and is_dataclass(widget.field_type) and field_value is not None:
                # For nested dataclass containers, update the label
                for child in widget.children():
                    if isinstance(child, QLabel):
                        child.setText("(edited)")
                        break
        
        self.valueChanged.emit()


class DataclassFormGenerator:
    """Generator for creating forms from dataclasses."""
    
    @staticmethod
    def create_form(dataclass_type: Type[T], parent=None) -> DataclassForm:
        """Create a form for the given dataclass type."""
        if not is_dataclass(dataclass_type):
            raise ValueError(f"{dataclass_type.__name__} is not a dataclass")
        
        form = DataclassForm(parent)
        
        # Get type hints for the dataclass
        type_hints = get_type_hints(dataclass_type)
        
        for f in fields(dataclass_type):
            field_name = f.name
            field_type = type_hints.get(field_name)
            
            # Skip internal fields
            if field_name.startswith('_'):
                continue
            
            # Create label with field name
            label = QLabel(field_name.replace('_', ' ').title())
            
            # Create appropriate widget based on field type
            widget = DataclassFormGenerator._create_widget_for_type(field_type, f.default, form)
            
            # Add to form
            form._layout.addRow(label, widget)
            form._widgets[field_name] = widget
            
            # Connect signals
            DataclassFormGenerator._connect_widget_signals(widget, form)
        
        form._dataclass_type = dataclass_type
        return form
    
    @staticmethod
    def _create_widget_for_type(field_type, default_value, parent):
        """Create an appropriate widget based on the field type."""
        origin = get_origin(field_type)
        args = get_args(field_type)
        
        # Handle Optional types
        if origin is Union and type(None) in args:
            # Get the non-None type
            real_type = next(arg for arg in args if arg is not type(None))
            return DataclassFormGenerator._create_widget_for_type(real_type, default_value, parent)
        
        # Handle basic types
        if field_type == str:
            widget = QLineEdit(parent)
            if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                widget.setText(str(default_value))
            return widget
        
        elif field_type == int:
            widget = QSpinBox(parent)
            widget.setRange(-1000000, 1000000)  # Reasonable default range
            if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                widget.setValue(default_value)
            return widget
        
        elif field_type == float:
            widget = QDoubleSpinBox(parent)
            widget.setRange(-1000000, 1000000)  # Reasonable default range
            widget.setDecimals(2)
            if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                widget.setValue(default_value)
            return widget
        
        elif field_type == bool:
            widget = QCheckBox(parent)
            if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                widget.setChecked(default_value)
            return widget
        
        # Handle lists
        elif origin is list:
            if args and args[0] == str:
                # Create a list widget with add/remove buttons
                container = QWidget(parent)
                layout = QVBoxLayout(container)
                layout.setContentsMargins(0, 0, 0, 0)
                
                list_widget = QListWidget(container)
                layout.addWidget(list_widget)
                
                # Add buttons for managing the list
                buttons_layout = QHBoxLayout()
                add_button = QPushButton("Add", container)
                remove_button = QPushButton("Remove", container)
                buttons_layout.addWidget(add_button)
                buttons_layout.addWidget(remove_button)
                layout.addLayout(buttons_layout)
                
                # Connect buttons
                add_button.clicked.connect(lambda: DataclassFormGenerator._add_list_item(list_widget))
                remove_button.clicked.connect(lambda: DataclassFormGenerator._remove_list_item(list_widget))
                
                # Initialize with default values if any
                if default_value is not None and default_value != field(default_factory=list) and hasattr(default_value, '__iter__'):
                    for item in default_value:
                        list_widget.addItem(str(item))
                
                return list_widget
            else:
                # For other types of lists, fallback to a text edit with comma-separated values
                widget = QTextEdit(parent)
                widget.setPlaceholderText("Enter comma-separated values")
                if default_value is not None and default_value != field(default_factory=list) and hasattr(default_value, '__iter__'):
                    widget.setPlainText(", ".join(str(x) for x in default_value))
                return widget
        
        # Handle nested dataclasses
        elif is_dataclass(field_type):
            # Create a button that opens a dialog with the nested form
            container = QWidget(parent)
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            value_label = QLabel("(click to edit)", container)
            edit_button = QPushButton("Edit", container)
            layout.addWidget(value_label, 1)
            layout.addWidget(edit_button)
            
            # Store the field type for later form creation
            container.field_type = field_type
            
            # Connect button to open dialog
            edit_button.clicked.connect(
                lambda field_type=field_type: DataclassFormGenerator._open_nested_form_dialog(
                    field_type, parent, value_label
                )
            )
            
            return container
        
        # Default fallback for unknown types
        widget = QLineEdit(parent)
        if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
            widget.setText(str(default_value))
        return widget
    
    @staticmethod
    def _connect_widget_signals(widget, form):
        """Connect appropriate signals from the widget to the form's valueChanged signal."""
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QTextEdit):
            widget.textChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
            widget.valueChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QListWidget):
            widget.model().rowsInserted.connect(form.valueChanged.emit)
            widget.model().rowsRemoved.connect(form.valueChanged.emit)
        elif isinstance(widget, DataclassForm):
            widget.valueChanged.connect(form.valueChanged.emit)
        elif hasattr(widget, 'form') and isinstance(widget.form, DataclassForm):
            widget.form.valueChanged.connect(form.valueChanged.emit)
    
    @staticmethod
    def _add_list_item(list_widget):
        """Add a new item to the list widget."""
        list_widget.addItem("New Item")
        # Make the new item editable
        item = list_widget.item(list_widget.count() - 1)
        list_widget.editItem(item)
    
    @staticmethod
    def _remove_list_item(list_widget):
        """Remove the selected item from the list widget."""
        selected_items = list_widget.selectedItems()
        if selected_items:
            for item in selected_items:
                list_widget.takeItem(list_widget.row(item))
    
    @staticmethod
    def _open_nested_form_dialog(field_type, parent, value_label=None):
        """Open a dialog with the nested form."""
        dialog = QDialog(parent)
        dialog.setWindowTitle(f"Edit {field_type.__name__}")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Create a new form each time the dialog is opened
        nested_form = DataclassFormGenerator.create_form(field_type, dialog)
        
        # If there's an existing value in the parent form, try to get it
        if hasattr(parent, 'get_value') and callable(parent.get_value):
            try:
                parent_value = parent.get_value()
                # Find the field that matches our field_type
                for field_name, field_value in inspect.getmembers(parent_value):
                    if not field_name.startswith('_') and isinstance(field_value, field_type):
                        nested_form.set_value(field_value)
                        break
            except Exception:
                # If we can't get the parent value, just continue with defaults
                pass
        
        # Add the form to a scroll area
        scroll = QScrollArea(dialog)
        scroll.setWidgetResizable(True)
        scroll.setWidget(nested_form)
        layout.addWidget(scroll)
        
        # Add OK/Cancel buttons
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)
        
        # Connect buttons
        ok_button.clicked.connect(dialog.accept)
        cancel_button.clicked.connect(dialog.reject)
        
        # Show the dialog
        result = dialog.exec_()
        
        if result == QDialog.Accepted and value_label:
            # Update the value label to show that the nested form has been edited
            value_label.setText("(edited)")
