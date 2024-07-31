"""
================================================================================================================
GUI Functions Library
================================================================================================================
    Created by G.H. Allison, University of Sheffield, Sheffield, United Kingdom.
    Copyright (C) 2024 George H. Allison
    Contact: ghallison1@sheffield.ac.uk or xinshan.li@sheffield.ac.uk
----------------------------------------------------------------------------------------------------------------

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

________________________________________________________________________________________________________________
"""

from PyQt6.QtWidgets import QApplication, QLabel, QPushButton, QLineEdit, QDoubleSpinBox, QSpinBox, QVBoxLayout, \
    QHBoxLayout, QFileDialog, QComboBox, QCheckBox
import logging
import numpy as np
from concurrent.futures import ThreadPoolExecutor
from stl import mesh
import os
from core_libs import waitingspinnerwidget


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


def browse_dir_path(text, var_target, var_key, line_edit_name, parent_widget):
    """
    Browse for a directory path and update the variable and widget
    :param text:  The dialog caption
    :param var_target:  The target object containing the variable
    :param var_key:  The key of the variable to update
    :param line_edit_name:  The object name of the QLineEdit widget
    :param parent_widget:  The parent widget containing the QLineEdit widget
    """
    path_name = QFileDialog.getExistingDirectory(caption=text)  # Open the file dialog
    if path_name:
        try:
            setattr(var_target, var_key, path_name)  # Set the variable value
        except Exception as e:
            print(f"Error setting value: {e}")
        update_line_edit(path_name, line_edit_name, parent_widget)


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


def on_value_changed(new_value, var_instance, var_name):
    """
    Update the value of the variable when the value of the widget changes
    :param new_value:  The new value of the widget
    :param var_instance:  The instance of the variable
    :param var_name:  The name of the variable
    """
    try:
        setattr(var_instance, var_name, new_value)
    except Exception as e:
        print(f"Error setting value: {e}")


def on_state_changed(state, var_instance, var_name):
    """
    Update the state of the variable when the state of the checkbox changes
    :param state:  The new state of the widget
    :param var_instance:  The instance of the variable
    :param var_name:  The name of the variable
    """
    try:
        setattr(var_instance, var_name, state == 2)
    except Exception as e:
        print(f"Error setting value: {e}")


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
            button.setObjectName(element_info.get('obname', ''))
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


def build_layout(layout_info):
    """
    Recursively builds layouts and their child widgets/layouts from a nested dictionary.
    """
    layout_type = layout_info.get('type', 'QVBoxLayout')  # Default to QVBoxLayout
    layout = QVBoxLayout() if layout_type == 'QVBoxLayout' else QHBoxLayout()

    for item in layout_info.get('items', []):
        if 'type' in item and item['type'] in ['QVBoxLayout', 'QHBoxLayout']:
            # Recursive case: item is a layout
            layout.addLayout(build_layout(item))
        else:
            # Base case: item is a widget
            signal_slots = item.get('slots')
            widget = create_gui_element(item, signal_slots=signal_slots)
            if widget:
                layout.addWidget(widget)

    return layout


def crossing(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    # Fixes a bug in numpy's cross product function where IDEs think it gives NoReturn
    return np.cross(a, b)


def load_stl(file_path):
    # Load STL file using numpy-stl
    try:
        mesh_data = mesh.Mesh.from_file(file_path)
    except Exception as e:
        print(f"Error loading STL file: {e}")
        return None  # Return None if an error occurs
    return mesh_data  # Return the mesh data if successful


def rotate_stl_180_z(stl_path):
    # Load the STL file
    model_mesh = load_stl(stl_path)

    # Define the rotation matrix for 180 degrees rotation around Z-axis
    rotation_matrix = np.array([[-1, 0, 0], [0, -1, 0], [0, 0, 1]])

    # Apply the rotation to each vertex
    model_mesh.vectors = np.dot(model_mesh.vectors, rotation_matrix)

    # Return the rotated mesh object
    return model_mesh


def check_stl_file_type(stl_path):
    try:
        with open(stl_path, 'rb') as file:
            header = file.read(80)  # Read the 80-byte header
            # Check if the header starts with 'solid ' indicating a potential ASCII file
            # Some binary files may also start with 'solid '
            if header.startswith(b'solid '):
                # Perform a simple check to see if the rest of the file looks like ASCII
                # This checks for the presence of 'facet normal' which is common in ASCII STLs
                file.seek(0)  # Go back to the beginning of the file
                contents = file.read(1024).lower()  # Read the first 1024 bytes
                if b'facet normal' in contents:
                    return 'ASCII'

            # Proceed with binary file size check
            triangles = int.from_bytes(file.read(4), byteorder='little')  # Read the number of triangles
            expected_size = 84 + (50 * triangles)  # Calculate the expected size for a binary STL

            file.seek(0, 2)  # Move to the end of the file
            actual_size = file.tell()  # Get the actual size of the file

            # Check if the actual size matches the expected size for a binary STL
            if actual_size == expected_size:
                return 'BINARY'
            else:
                # If the size doesn't match, it's safer to assume ASCII
                # This could also indicate a malformed file
                return 'ASCII'
    except Exception as e:
        print(f"Error checking STL file type: {e}")
        # In case of an error, it might be safer to default to ASCII or handle the error explicitly
        return 'ASCII'


def dir_check_and_make(make_name, check_dir):
    """
    This function checks for the existence of a directory and creates it if it doesn't exist.
    :param make_name:  The name of the directory to create
    :param check_dir:  The directory to check for the existence of the new directory
    :return: make_dir:  The directory path created
    """
    try:
        make_dir = os.path.join(check_dir, make_name)  # Create the directory path
    except Exception as e:
        print(f"Error creating directory path: {e}")
        return None
    try:
        os.makedirs(make_dir, exist_ok=True)  # Create the directory if it doesn't exist
    except Exception as e:
        print(f"Error creating directory {make_dir}: {e}")
        return None
    return make_dir


def throbbing(parent_widget):
    """
    Finds the throbber widget and changes its current state.

    :param parent_widget: The parent widget where the throbber is located.
    """
    throbber = parent_widget.findChild(waitingspinnerwidget.QtWaitingSpinner, 'throbr')  # Find the throbber widget
    match throbber.isSpinning():  # Check the current state of the throbber
        case True:
            throbber.stop()
        case False:
            throbber.start()
        case _:
            print("Error: Throbber not found.")


def gen_thread_worker(func, active_cores):
    """
    Generate a thread worker for a function.
    :param func: The function to run in the thread worker.
    :param active_cores: The number of active cores.
    """

    work_cores = max(1, int(os.cpu_count()) - (int(active_cores) + 1)) # Calculate the number of worker cores, return at least 1
    executer = ThreadPoolExecutor(max_workers=int(work_cores))  # Create a thread executor
    throb_core = ThreadPoolExecutor(max_workers=1)

    main_window = QApplication.instance().main_window  # Get the main window
    input_widgets = main_window.findChildren((QLineEdit, QDoubleSpinBox, QSpinBox, QComboBox, QPushButton, QCheckBox))  # Find all input widgets

    for widget in input_widgets:
        widget.setEnabled(False)

    try:
        throb_core.submit(throbbing(main_window))  # Start the throbber
        future = executer.submit(func)  # Submit the function to the executor

        def callback(future):
            try:
                future.result()  # Attempt to retrieve the result, which will re-raise any exception caught during execution
            except Exception as e:
                logging.error(f"Error in thread worker function: {e}")  # Log the error
            finally:
                throbbing(main_window)  # Ensure the throbber stops
                for widget in input_widgets:
                    widget.setEnabled(True)

        future.add_done_callback(callback)  # Add the callback to the future
    except Exception as e:
        logging.error(f"Error starting thread worker: {e}")  # Log the error
        for widget in input_widgets:
            widget.setEnabled(True)
    finally:
        throb_core.shutdown(wait=False)  # Shutdown the throbber executor
        executer.shutdown(wait=False)  # Shutdown the executor
