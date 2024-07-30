# Customisation

This section discusses customising the program to suit your own needs. This includes creating your own scripts.

Custom scripts can be created by anyone and used by inserting that script in the corresponding folder and 
restarting the program.

## Creating Custom Scripts

Custom scripts can be created for all tabs, but have two minimum requirements for functionality. A name from the 
function `get_name()` and a GUI structure from the function `gui_elements()`. 
This allows the program to switch tab elements dynamically as you load alternative scripts.

See examples below:

```python
def get_name():
    return "Display Name for your script"
```

```python
def gui_elements():
    gui_structure = {
        'type': 'QVBoxLayout',  # Top-level layout
        'items': [
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'FEM File Directory:'
                    },
                    {
                        'type': 'QLineEdit',
                        'placeholder': 'FEM File Directory Path'
                        'obname': 'fem_file_dir',
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {'clicked': update_label}
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Filename:'
                    },
                    {
                        'type': 'QLineEdit',
                        'placeholder': 'FEM File Name',
                        'obname': 'fem_file_name',
                        'slots': {
                            'valueChanged': ('id', var_ins, lambda value: on_value_changed(value, var_ins, 'id'))
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Force (N):'
                    },
                    {
                        'type':'QDoubleSpinBox',
                        'min': 0,
                        'max': 100000,
                        'value': var_ins.F,
                        'step': 1,
                        'dp': 2,
                        'slots': {
                            'valueChanged': ('F', var_ins, lambda value: on_value_changed(value, var_ins, 'F'))
                        }
                    }
                ]
            },
            {
                'type': 'QPushButton',
                'text': 'FEM Analysis',
                'slots': {'clicked': update_label}
            }
        ]
    }
    return gui_structure
```

## Linking UI Elements to Functions

To link UI elements to functions, you can use the `slots` key in the `gui_elements()` function. This key is a dictionary
of the signal and the function to call when the signal is emitted. Standard signals include `clicked`, `valueChanged`.

### Clicked Signal

The `clicked` signal is emitted when the button is clicked. This can be linked to a function to perform an action.

```python
{
    'type': 'QPushButton',
    'text': 'FEM Analysis',
    'slots': {'clicked': update_label}
}
```

### Value Changed Signal

The `valueChanged` signal is emitted when the value of the element changes. This can be linked to a function to update
a variable or perform an action.

```python
{
    'type':'QDoubleSpinBox',
    'min': 0,
    'max': 100000,
    'value': var_ins.F,
    'step': 1,
    'dp': 2,
    'slots': {
        'valueChanged': ('F', var_ins, lambda value: on_value_changed(value, var_ins, 'F'))
    }
}
```

### Custom Clicked Functions

Some custom functions are defined to make certain actions easier like browsing for a file.

```python
def browse_file_path(text, var_target, var_key, file_types, line_edit_name, parent_widget):
    """
    Browse for a file path and update the variable and widget
    :param text:  The dialog caption
    :param var_target:  The target object containing the variable
    :param var_key:  The key of the variable to update
    :param file_types:  The file types to filter
    :param line_edit_name:  The object name of the QLineEdit widget
    :param parent_widget:  The parent widget containing the QLineEdit widget
    """
    file_name, _ = QFileDialog.getOpenFileName(caption=text, filter=file_types)
    if file_name:
        try:
            setattr(var_target, var_key, file_name)
        except Exception as e:
            print(f"Error setting value: {e}")
        update_line_edit(file_name, line_edit_name, parent_widget)
```

### Parent Widget and Object Name

The `parent_widget` and `line_edit_name` are used to update the widget with the new value. This is done by finding the
widget by name in the parent widget and updating the text.

```python
def update_line_edit(text, line_edit_name, parent_widget):
    """
    Update the text of a QLineEdit widget
    :param text:  The new text to set
    :param line_edit_name:  The object name of the QLineEdit widget
    :param parent_widget:  The parent widget containing the QLineEdit widget
    """
    line_edit = parent_widget.findChild(QLineEdit, line_edit_name)  # Find the QLineEdit widget
    if isinstance(line_edit, QLineEdit):
        try:
            line_edit.setText(text)
        except Exception as e:
            print(f"Error setting text: {e}")
    else:
        print(f"Expected a QLineEdit instance, got {type(line_edit)} instead.")
```

It is important to note that the `parent_widget` is the top-level widget containing the widget you want to update. This
is often the `QDialog` or `QMainWindow` instance. Make sure you are passing the correct parent widget. As using 
`self` in the function will generally not work, `QCoreApplication.instance().activeWindow()` will only work when the
window is focused.

The `line_edit_name` is the object name of the widget you want to update. This is set in the `obname` key in the
`gui_funcs.py` file in core_libs.


## Custom GUI Build Function

The `create_gui_element()` function is a factory function to create GUI elements based on the provided info. 
This function is used to create the GUI elements from the `gui_elements()` function. It is a switch statement that
creates the appropriate widget based on the type provided. 

It is not exhaustive and can be expanded to include more widget types.

```python
def create_gui_element(element_info, signal_slots=None):
    """
    Factory function to create GUI elements based on the provided info.
    """
    element_type = element_info.get('type')
    match element_type:
        case 'QLabel':
            return QLabel(element_info.get('text', ''))
        case 'QPushButton':
            button = QPushButton(element_info.get('text', ''))
            if signal_slots and 'clicked' in signal_slots:
                button.clicked.connect(signal_slots['clicked'])
            return button
        case 'QLineEdit':
            widget = QLineEdit()
            widget.setObjectName(element_info.get('obname', ''))
            widget.setPlaceholderText(element_info.get('placeholder', ''))
            widget.setText(element_info.get('text', ''))
            if signal_slots and 'valueChanged' in signal_slots:
                var_name, var_inst, slot_func = signal_slots['valueChanged']
                if hasattr(var_inst, var_name):
                    widget.setText(getattr(var_inst, var_name))
                widget.textChanged.connect(lambda value, vn=var_name, vi=var_inst: on_value_changed(value, vi, vn))
            return widget
        case 'QDoubleSpinBox':
            widget = QDoubleSpinBox()
            widget.setRange(element_info.get('min', 0.00), element_info.get('max', 100000.00))
            widget.setValue(element_info.get('value', 0.00))
            widget.setSingleStep(element_info.get('step', 1.00))
            widget.setDecimals(element_info.get('dp', 2))
            if signal_slots and 'valueChanged' in signal_slots:
                var_name, var_inst, slot_func = signal_slots['valueChanged']
                widget.valueChanged.connect(lambda value, vn=var_name, vi=var_inst: on_value_changed(value, vi, vn))
            return widget
        case 'QSpinBox':
            widget = QSpinBox()
            widget.setRange(element_info.get('min', 0), element_info.get('max', 100000))
            widget.setValue(element_info.get('value', 0))
            widget.setSingleStep(element_info.get('step', 1))
            if signal_slots and 'valueChanged' in signal_slots:
                var_name, var_inst, slot_func = signal_slots['valueChanged']
                widget.valueChanged.connect(lambda value, vn=var_name, vi=var_inst: on_value_changed(value, vi, vn))
            return widget
        case 'QComboBox':
            widget = QComboBox()
            widget.setObjectName(element_info.get('obname', ''))
            widget.addItem(element_info.get('placeholder', ''))
            if signal_slots and 'valueChanged' in signal_slots:
                var_name, var_inst, slot_func = signal_slots['valueChanged']
                widget.currentIndexChanged.connect(lambda value, vn=var_name, vi=var_inst: on_value_changed(value, vi, vn))
            return widget
        case _:
            return None
```
