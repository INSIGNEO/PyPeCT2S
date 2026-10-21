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
var_ins = core_libs.mat_vars.LUMAVariables()
gui_ins = core_libs.gui_vars.GuiVariables()


def get_name():
    return "LUMA"


def gui_elements():
    gui_structure = {
        'type': 'QVBoxLayout',  # Top-level layout
        'items': [
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Image File:'
                    },
                    {
                        'type': 'QLineEdit',
                        'obname': 'imagefile',
                        'placeholder': 'image File Path',
                        'text': var_ins.image_path,
                        'slots': {
                            'valueChanged': (
                                'image_path', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'image_path')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_file_path('Select Image File', var_ins, 'image_path',
                                                                             'VTK Files (*.vtk);;'
                                                                             'DICOM Files (*.dcm *.dicom);;'
                                                                             'NIfTI Files (*.nii *.nii.gz);;'
                                                                             'NRRD Files (*.nrrd *.nhdr);;'
                                                                             'All Files (*)',
                                                                             'imagefile', QApplication.instance().main_window)
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
                        'text': var_ins.mesh_path,
                        'slots': {
                            'valueChanged': (
                                'mesh_path', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'mesh_path')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_file_path('Select Mesh File', var_ins, 'mesh_path',
                                                                             'ANSYS CDB Files (*.cdb);;'
                                                                             'All Files (*)',
                                                                             'meshfile', QApplication.instance().main_window)
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
                                lambda: core_libs.gui_funcs.browse_file_path('Select Config File', var_ins, 'config_path', 'Config Files (*.toml);;All Files (*)', 'configfile', QApplication.instance().main_window)
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QCheckBox',
                        'text': 'Visualise Output',
                        'obname': 'visualise_check',
                        'slots': {
                            'stateChanged': (
                                'visualise_output', var_ins, lambda state: core_libs.gui_funcs.on_value_changed(state == 2, var_ins, 'visualise_output')
                            )
                        }
                    },
                    {
                        'type': 'QCheckBox',
                        'text': 'Save Histogram',
                        'obname': 'histogram_check',
                        'slots': {
                            'stateChanged': (
                                'save_histogram', var_ins, lambda state: core_libs.gui_funcs.on_value_changed(state == 2, var_ins, 'save_histogram')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'LUMA Material Application',
                        'slots': {
                            'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(auto_luma, gui_ins.core_count)
                        }
                    }
                ]
            },
        ]
    }
    return gui_structure


def auto_luma():
    print("Running LUMA...")
    # check that luma is installed and accessible on system path
    try:
        subprocess.run(["luma", "--version"], check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print("Error: LUMA is not installed or not accessible on the system path.\nPlease install LUMA from https://luma.haivu.org and ensure it is in your PATH.")
        return
    except PermissionError:
        print("Error: Permission denied when trying to run LUMA.\nPlease check your permissions and ensure that LUMA is executable.")
        return
    except subprocess.CalledProcessError as e:
        print(f"Error: LUMA was found, but `luma --version` failed: {e.stderr.strip()}")
        return

    else:
        try:
            # Define the command and arguments
            command = "luma"
            image_command = "--ct"
            mesh_command = "--mesh"
            params_command = "--params"
            image_arg = var_ins.image_path
            mesh_arg = var_ins.mesh_path
            params_arg = var_ins.config_path
            if var_ins.visualise_output:
                vis_arg = "--visualise"
            if var_ins.save_histogram:
                hist_arg = "--histogram"

            # Run the subprocess
            match (var_ins.visualise_output, var_ins.save_histogram):
                case (True, True):
                    bone = subprocess.run([command, image_command, image_arg, mesh_command, mesh_arg, params_command, params_arg, vis_arg, hist_arg], capture_output=True, text=True)
                case (True, False):
                    bone = subprocess.run([command, image_command, image_arg, mesh_command, mesh_arg, params_command, params_arg, vis_arg], capture_output=True, text=True)
                case (False, True):
                    bone = subprocess.run([command, image_command, image_arg, mesh_command, mesh_arg, params_command, params_arg, hist_arg], capture_output=True, text=True)
                case (False, False):
                    bone = subprocess.run([command, image_command, image_arg, mesh_command, mesh_arg, params_command, params_arg], capture_output=True, text=True)
            print(bone.stdout)
            print(bone.stderr)
        except Exception as e:
            print(f"Error: {e}\nLUMA has failed to run please check you have files in the correct location")
        else:
            print("LUMA has finished!")
