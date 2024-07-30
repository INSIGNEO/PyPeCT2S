"""
================================================================================================================
Bonemat Command Line Interface (CLI) Based Functions
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

import os
import subprocess
import glob
from PyQt6.QtWidgets import QApplication
import core_libs
from core_libs import *

# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'cdb FEM Files (*.cdb);;DB FEM Files (*.db);;All Files (*)', 'ffdir', QApplication.instance().main_window) # for browse_file_path
# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'ffdir', QApplication.instance().main_window) # for browse_dir_path
var_ins = core_libs.mat_vars.BMatVariables()
gui_ins = core_libs.gui_vars.GuiVariables()


def get_name():
    return "Bonemat"


def gui_elements():
    gui_structure = {
        'type': 'QVBoxLayout',  # Top-level layout
        'items': [
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'VTK File:'
                    },
                    {
                        'type': 'QLineEdit',
                        'obname': 'vtkfile',
                        'placeholder': 'VTK File Path',
                        'text': var_ins.vtk_path,
                        'slots': {
                            'valueChanged': (
                                'vtk_path', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'vtk_path')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_file_path('Select VTK image File', var_ins, 'vtk_path', 'VTK Files (*.vtk);;All Files (*)', 'vtkfile', QApplication.instance().main_window)
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Mesh File:'
                    },
                    {
                        'type': 'QLineEdit',
                        'obname': 'meshfile',
                        'placeholder': 'Mesh file path',
                        'text': var_ins.cdb_path,
                        'slots': {
                            'valueChanged': (
                                'cdb_path', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'cdb_path')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_file_path('Select Mesh File', var_ins, 'cdb_path', 'ANSYS CDB Files (*.cdb);;All Files (*)', 'meshfile', QApplication.instance().main_window)
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Config File:'
                    },
                    {
                        'type': 'QLineEdit',
                        'obname': 'configfile',
                        'placeholder': 'Config file path',
                        'text': var_ins.config_path,
                        'slots': {
                            'valueChanged': (
                                'config_path', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'config_path')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_file_path('Select Config File', var_ins, 'config_path', 'Config Files (*.xml);;All Files (*)', 'configfile', QApplication.instance().main_window)
                        }
                    }
                ]
            },
            {
                'type': 'QPushButton',
                'text': 'Bonemat Material Application',
                'slots': {
                    'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(auto_bonemat, gui_ins.core_count)
                }
            }
        ]
    }
    return gui_structure


def auto_bonemat():
    print("Running Auto Bonemat...")
    try:
        # Define the command and arguments
        filename_without_extension = os.path.splitext(os.path.basename(var_ins.cdb_path))[0]
        command = os.path.join(gui_ins.app_path, "bonemat/BonematCLI.exe")
        arg1 = var_ins.vtk_path
        arg2 = var_ins.cdb_path
        arg3 = var_ins.config_path
        arg4 = f"{gui_ins.save_path}/{filename_without_extension}-mat.cdb"

        # Run the subprocess
        bone = subprocess.run([command, arg1, arg2, arg3, arg4], capture_output=True, text=True)
        print(bone.stdout)
        print(bone.stderr)
        print("Auto Bonemat has finished successfully!")
    except Exception as e:
        print(f"Error: {e}\n Auto Bonemat has failed to run please check you have files in the correct location")
