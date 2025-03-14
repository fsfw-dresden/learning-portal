"""
Form generator for dataclasses.
"""

import inspect
import logging
import dataclasses
from dataclasses import field, fields, is_dataclass, MISSING

# Set up logging
logger = logging.getLogger(__name__)
from typing import Type, TypeVar, Union, get_type_hints, get_origin, get_args

from .widget_interfaces import ListWidgetBase

# Field metadata for form generation
class FormField:
    """Metadata for form fields"""
    
    @staticmethod
    def number(min_value=None, max_value=None, use_slider=False, orientation=None):
        """
        Create metadata for a number field with min/max constraints
        
        Args:
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            use_slider: If True, use a slider instead of a spin box
            orientation: Optional slider orientation ('horizontal' or 'vertical')
        """
        return {"form_field": {
            "min": min_value, 
            "max": max_value,
            "use_slider": use_slider,
            "orientation": orientation
        }}
    
    @staticmethod
    def text(placeholder=None, multiline=False):
        """Create metadata for a text field"""
        return {"form_field": {"placeholder": placeholder, "multiline": multiline}}
    
    @staticmethod
    def options(choices=None):
        """Create metadata for a field with predefined choices"""
        return {"form_field": {"choices": choices or []}}

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QCheckBox, QComboBox, QDialog, QDoubleSpinBox, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QScrollArea, QSpinBox,
    QSlider, QTextEdit, QVBoxLayout, QWidget
)
from PyQt5.QtCore import Qt

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
            elif isinstance(widget, QWidget) and hasattr(widget, 'slider'):
                # Handle slider widgets
                if hasattr(widget, 'slider_to_float'):
                    # Float slider
                    values[field_name] = widget.slider_to_float(widget.slider.value())
                else:
                    # Integer slider
                    values[field_name] = widget.slider.value()
            elif isinstance(widget, QCheckBox):
                values[field_name] = widget.isChecked()
            elif isinstance(widget, QComboBox):
                values[field_name] = widget.currentText()
            elif isinstance(widget, ListWidgetBase):
                values[field_name] = widget.get_items()
            elif isinstance(widget, QListWidget):
                items = []
                for i in range(widget.count()):
                    items.append(widget.item(i).text())
                values[field_name] = items
            elif isinstance(widget, DataclassForm):
                values[field_name] = widget.get_value()
            elif hasattr(widget, 'field_type') and is_dataclass(widget.field_type):
                # For nested dataclass containers, use the stored value if available
                if hasattr(widget, 'field_value'):
                    values[field_name] = widget.field_value
                else:
                    # Create a default instance as fallback
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
            elif isinstance(widget, QWidget) and hasattr(widget, 'slider'):
                # Handle slider widgets
                if hasattr(widget, 'slider_to_float'):
                    # Float slider - need to convert float to slider value
                    min_value = widget.slider.minimum()
                    max_value = widget.slider.maximum()
                    range_value = max_value - min_value
                    
                    # Get min/max from the original range
                    slider_min = widget.slider.minimum()
                    slider_max = widget.slider.maximum()
                    
                    # Convert float to slider value (0-100)
                    if hasattr(widget, 'float_to_slider'):
                        slider_value = widget.float_to_slider(field_value)
                    else:
                        # Fallback calculation if float_to_slider not available
                        slider_value = int(((field_value - slider_min) / (slider_max - slider_min)) * range_value)
                        slider_value = max(min_value, min(slider_value, max_value))
                    
                    widget.slider.setValue(slider_value)
                    widget.value_label.setText(str(field_value))
                else:
                    # Integer slider
                    widget.slider.setValue(field_value)
                    widget.value_label.setText(str(field_value))
            elif isinstance(widget, QCheckBox):
                widget.setChecked(field_value)
            elif isinstance(widget, QComboBox):
                index = widget.findText(str(field_value))
                if index >= 0:
                    widget.setCurrentIndex(index)
            elif isinstance(widget, ListWidgetBase):
                widget.set_items(field_value)
            elif isinstance(widget, QListWidget):
                widget.clear()
                for item in field_value:
                    widget.addItem(str(item))
            elif isinstance(widget, DataclassForm):
                widget.set_value(field_value)
            elif hasattr(widget, 'field_type') and is_dataclass(widget.field_type) and field_value is not None:
                # For nested dataclass containers, store the value and update the label
                widget.field_value = field_value
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
            
            # Log field information
            logger.debug(f"Processing field: {field_name}, type: {field_type}")
            logger.debug(f"Field default: {f.default}")
            logger.debug(f"Field metadata: {f.metadata if hasattr(f, 'metadata') else 'No metadata'}")
            
            # Create label with field name
            label = QLabel(field_name.replace('_', ' ').title())
            
            # Create appropriate widget based on field type
            widget = DataclassFormGenerator._create_widget_for_type(field_type, f, form)
            
            # Add to form
            form._layout.addRow(label, widget)
            form._widgets[field_name] = widget
            
            # Connect signals
            DataclassFormGenerator._connect_widget_signals(widget, form)
        
        form._dataclass_type = dataclass_type
        return form
    
    @staticmethod
    def _create_widget_for_type(field_type, field_obj, parent):
        """Create an appropriate widget based on the field type."""
        origin = get_origin(field_type)
        args = get_args(field_type)
        
        # Handle Optional types
        if origin is Union and type(None) in args:
            # Get the non-None type
            real_type = next(arg for arg in args if arg is not type(None))
            # Pass the same field_obj, not just its default value
            return DataclassFormGenerator._create_widget_for_type(real_type, field_obj, parent)
        
        # Get default value after handling Optional types
        default_value = field_obj.default if hasattr(field_obj, 'default') else None
        
        # Handle basic types
        if field_type == str:
            # Check if this should be a multiline text field
            multiline = False
            if hasattr(field_obj, 'metadata') and 'form_field' in field_obj.metadata:
                form_field = field_obj.metadata['form_field']
                if 'multiline' in form_field and form_field['multiline']:
                    multiline = True
                    
            if multiline:
                widget = QTextEdit(parent)
                if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                    widget.setPlainText(str(default_value))
                
                # Set placeholder text if provided
                if hasattr(field_obj, 'metadata') and 'form_field' in field_obj.metadata:
                    form_field = field_obj.metadata['form_field']
                    if 'placeholder' in form_field and form_field['placeholder']:
                        widget.setPlaceholderText(form_field['placeholder'])
            else:
                widget = QLineEdit(parent)
                if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                    widget.setText(str(default_value))
                
                # Set placeholder text if provided
                if hasattr(field_obj, 'metadata') and 'form_field' in field_obj.metadata:
                    form_field = field_obj.metadata['form_field']
                    if 'placeholder' in form_field and form_field['placeholder']:
                        widget.setPlaceholderText(form_field['placeholder'])
            
            return widget
        
        elif field_type == int:
            # Default range
            min_value = -1000000
            max_value = 1000000
            use_slider = False
            orientation = None
            
            # Check for metadata with min/max constraints
            logger.debug(f"Field type: {field_type}, Default value: {default_value}")
            logger.debug(f"Field object: {field_obj}")
            logger.debug(f"Has metadata: {hasattr(field_obj, 'metadata')}")
            
            if hasattr(field_obj, 'metadata') and 'form_field' in field_obj.metadata:
                form_field = field_obj.metadata['form_field']
                logger.debug(f"Form field metadata: {form_field}")
                
                if 'min' in form_field and form_field['min'] is not None:
                    min_value = form_field['min']
                    logger.debug(f"Setting min value to {min_value}")
                    
                if 'max' in form_field and form_field['max'] is not None:
                    max_value = form_field['max']
                    logger.debug(f"Setting max value to {max_value}")
                
                if 'use_slider' in form_field and form_field['use_slider']:
                    use_slider = True
                    logger.debug("Using slider instead of spin box")
                
                if 'orientation' in form_field and form_field['orientation']:
                    orientation = form_field['orientation']
                    logger.debug(f"Setting slider orientation to {orientation}")
            
            logger.info(f"Setting range for {field_type} field: min={min_value}, max={max_value}")
            
            if use_slider:
                # Create a container widget with a slider and a value label
                container = QWidget(parent)
                
                # Choose orientation
                slider_orientation = Qt.Horizontal
                if orientation == 'vertical':
                    slider_orientation = Qt.Vertical
                    container_layout = QVBoxLayout(container)
                else:
                    container_layout = QHBoxLayout(container)
                
                container_layout.setContentsMargins(0, 0, 0, 0)
                
                # Create slider
                slider = QSlider(slider_orientation, container)
                slider.setRange(min_value, max_value)
                slider.setTickPosition(QSlider.TicksBelow)
                
                # Create value label
                value_label = QLabel(str(min_value), container)
                value_label.setMinimumWidth(40)
                
                # Add widgets to layout
                container_layout.addWidget(slider)
                container_layout.addWidget(value_label)
                
                # Connect slider value changed to update label
                slider.valueChanged.connect(lambda v: value_label.setText(str(v)))
                
                # Set default value if provided
                if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                    if isinstance(default_value, int):
                        slider.setValue(default_value)
                        value_label.setText(str(default_value))
                    elif hasattr(default_value, 'default') and default_value.default != MISSING:
                        slider.setValue(default_value.default)
                        value_label.setText(str(default_value.default))
                
                # Store the slider in the container for value retrieval
                container.slider = slider
                container.value_label = value_label
                
                return container
            else:
                # Use regular spin box
                widget = QSpinBox(parent)
                widget.setRange(min_value, max_value)
                
                # Set default value if provided
                if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                    if isinstance(default_value, int):
                        widget.setValue(default_value)
                    elif hasattr(default_value, 'default') and default_value.default != MISSING:
                        widget.setValue(default_value.default)
                
                return widget
        
        elif field_type == float:
            # Default range
            min_value = -1000000
            max_value = 1000000
            use_slider = False
            orientation = None
            
            # Check for metadata with min/max constraints
            logger.debug(f"Float field type: {field_type}, Default value: {default_value}")
            logger.debug(f"Field object: {field_obj}")
            logger.debug(f"Has metadata: {hasattr(field_obj, 'metadata')}")
            
            if hasattr(field_obj, 'metadata') and 'form_field' in field_obj.metadata:
                form_field = field_obj.metadata['form_field']
                logger.debug(f"Form field metadata: {form_field}")
                
                if 'min' in form_field and form_field['min'] is not None:
                    min_value = form_field['min']
                    logger.debug(f"Setting min value to {min_value}")
                    
                if 'max' in form_field and form_field['max'] is not None:
                    max_value = form_field['max']
                    logger.debug(f"Setting max value to {max_value}")
                
                if 'use_slider' in form_field and form_field['use_slider']:
                    use_slider = True
                    logger.debug("Using slider instead of spin box")
                
                if 'orientation' in form_field and form_field['orientation']:
                    orientation = form_field['orientation']
                    logger.debug(f"Setting slider orientation to {orientation}")
            
            logger.info(f"Setting range for {field_type} field: min={min_value}, max={max_value}")
            
            if use_slider:
                # Create a container widget with a slider and a value label
                container = QWidget(parent)
                
                # Choose orientation
                slider_orientation = Qt.Horizontal
                if orientation == 'vertical':
                    slider_orientation = Qt.Vertical
                    container_layout = QVBoxLayout(container)
                else:
                    container_layout = QHBoxLayout(container)
                
                container_layout.setContentsMargins(0, 0, 0, 0)
                
                # For float sliders, we'll use 100 steps between min and max
                # and convert the integer slider value to float
                slider_range = 100
                
                # Create slider
                slider = QSlider(slider_orientation, container)
                slider.setRange(0, slider_range)
                slider.setTickPosition(QSlider.TicksBelow)
                
                # Create value label
                value_label = QLabel(str(min_value), container)
                value_label.setMinimumWidth(60)
                
                # Function to convert slider value to float
                def slider_to_float(slider_value):
                    # Map slider value (0-100) to the float range
                    float_value = min_value + (slider_value / slider_range) * (max_value - min_value)
                    # Round to 2 decimal places
                    return round(float_value, 2)
                
                # Function to convert float to slider value
                def float_to_slider(float_value):
                    # Map float value to slider range (0-100)
                    if max_value == min_value:
                        return 0
                    slider_value = int(((float_value - min_value) / (max_value - min_value)) * slider_range)
                    return max(0, min(slider_value, slider_range))
                
                # Add widgets to layout
                container_layout.addWidget(slider)
                container_layout.addWidget(value_label)
                
                # Connect slider value changed to update label
                slider.valueChanged.connect(
                    lambda v: value_label.setText(str(slider_to_float(v)))
                )
                
                # Set default value if provided
                if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                    if isinstance(default_value, float):
                        slider_value = float_to_slider(default_value)
                        slider.setValue(slider_value)
                        value_label.setText(str(default_value))
                    elif hasattr(default_value, 'default') and default_value.default != MISSING:
                        slider_value = float_to_slider(default_value.default)
                        slider.setValue(slider_value)
                        value_label.setText(str(default_value.default))
                
                # Store the slider and conversion functions in the container for value retrieval
                container.slider = slider
                container.value_label = value_label
                container.slider_to_float = slider_to_float
                
                return container
            else:
                # Use regular double spin box
                widget = QDoubleSpinBox(parent)
                widget.setRange(min_value, max_value)
                widget.setDecimals(2)
                
                # Set default value if provided
                if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                    if isinstance(default_value, float):
                        widget.setValue(default_value)
                    elif hasattr(default_value, 'default') and default_value.default != MISSING:
                        widget.setValue(default_value.default)
                
                return widget
        
        elif field_type == bool:
            widget = QCheckBox(parent)
            if default_value is not None and default_value != field(default_factory=list) and not isinstance(default_value, type(dataclasses.MISSING)):
                widget.setChecked(default_value)
            return widget
        
        # Handle lists
        elif origin is list:
            if args and args[0] == str:
                # Import here to avoid circular imports
                from .string_list_widget import StringListWidget
                
                # Create a StringListWidget for lists of strings
                default_items = []
                if default_value is not None and default_value != field(default_factory=list) and hasattr(default_value, '__iter__'):
                    default_items = default_value
                
                list_widget = StringListWidget(parent, default_items)
                return list_widget
            elif args and is_dataclass(args[0]):
                # Import here to avoid circular imports
                from .list_of_things_widget import ListOfThingsWidget
                
                # Create a ListOfThingsWidget for lists of dataclasses
                default_items = []
                if default_value is not None and default_value != field(default_factory=list) and hasattr(default_value, '__iter__'):
                    default_items = default_value
                
                list_widget = ListOfThingsWidget(args[0], parent, default_items)
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
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            
            value_label = QLabel("(click to edit)", container)
            edit_button = QPushButton("Edit", container)
            container_layout.addWidget(value_label, 1)
            container_layout.addWidget(edit_button)
            
            # Store the field type and a default instance for later form creation
            container.field_type = field_type
            # Create a default instance with empty values
            field_args = {}
            for f in fields(field_type):
                if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING:
                    field_type_hint = get_type_hints(field_type).get(f.name)
                    if field_type_hint == str:
                        field_args[f.name] = ""
                    elif field_type_hint == int:
                        field_args[f.name] = 0
                    elif field_type_hint == float:
                        field_args[f.name] = 0.0
                    elif field_type_hint == bool:
                        field_args[f.name] = False
                    elif get_origin(field_type_hint) is list:
                        field_args[f.name] = []
                    else:
                        field_args[f.name] = None
            container.field_value = field_type(**field_args)
            
            # Connect button to open dialog
            # Store field_type in a local variable to avoid lambda capture issues
            ft = field_type
            edit_button.clicked.connect(
                lambda checked=False, ft=ft: DataclassFormGenerator._open_nested_form_dialog(
                    ft, parent, value_label
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
        elif isinstance(widget, QWidget) and hasattr(widget, 'slider'):
            # Connect slider's valueChanged signal
            widget.slider.valueChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QCheckBox):
            widget.stateChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, ListWidgetBase):
            widget.valueChanged.connect(form.valueChanged.emit)
        elif isinstance(widget, QListWidget):
            widget.model().rowsInserted.connect(form.valueChanged.emit)
            widget.model().rowsRemoved.connect(form.valueChanged.emit)
        elif isinstance(widget, DataclassForm):
            widget.valueChanged.connect(form.valueChanged.emit)
        elif hasattr(widget, 'form') and isinstance(widget.form, DataclassForm):
            widget.form.valueChanged.connect(form.valueChanged.emit)
    
    @staticmethod
    def _handle_dialog_accept(dialog):
        """Handle the accept action for nested form dialogs."""
        # Get the form value
        if hasattr(dialog, 'nested_form') and dialog.nested_form:
            try:
                value = dialog.nested_form.get_value()
                
                # Store the value in the container widget
                if hasattr(dialog, 'container') and dialog.container:
                    dialog.container.field_value = value
                
                # Update the label
                if hasattr(dialog, 'value_label') and dialog.value_label:
                    dialog.value_label.setText("(edited)")
            except Exception as e:
                print(f"Error getting form value: {e}")
        
        # Accept the dialog
        dialog.accept()
    
    @staticmethod
    def _open_nested_form_dialog(field_type, parent, value_label=None):
        """Open a dialog with the nested form."""
        dialog = QDialog(parent)
        
        # Ensure field_type is a dataclass type
        if not is_dataclass(field_type):
            print(f"Error: Expected dataclass type, got {type(field_type)}")
            return
            
        dialog.setWindowTitle(f"Edit {field_type.__name__}")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout(dialog)
        
        # Create a new form each time the dialog is opened
        nested_form = DataclassFormGenerator.create_form(field_type, dialog)
        
        # Get the container widget that holds our field_type and field_value
        container = None
        if isinstance(parent, QWidget):
            # Find the container widget in the parent's hierarchy
            for widget in parent.findChildren(QWidget):
                if hasattr(widget, 'field_type') and widget.field_type == field_type:
                    container = widget
                    break
        
        # If we found the container with a stored value, use it
        if container and hasattr(container, 'field_value'):
            nested_form.set_value(container.field_value)
        
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
        
        # Store references for the accept handler
        dialog.nested_form = nested_form
        dialog.container = container
        dialog.value_label = value_label
        
        # Connect buttons with custom handlers
        ok_button.clicked.connect(lambda: DataclassFormGenerator._handle_dialog_accept(dialog))
        cancel_button.clicked.connect(dialog.reject)
        
        # Show the dialog
        dialog.exec_()
