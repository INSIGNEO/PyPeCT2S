"""
================================================================================================================
Python script to automate 4-point bending analysis in ANSYS APDL as part of the CT2S pipeline
================================================================================================================
    Created by G.H. Allison, University of Sheffield, Sheffield, United Kingdom.
    Initial creation date: 18-September-2026.
    Current version date: 18-September-2026
    Based on prior work by Dr. Xinshan Li and Dr. Zainab Altai.
    Copyright (C) 2026 George H. Allison
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
import datetime
import os
import traceback
from codecs import ignore_errors

import numpy as np
import time
import glob

from fem_libs.A_APDL_4B_fem_elem import bending, var_ins, gui_ins
from PyQt6.QtWidgets import QApplication
import psutil
import re
import core_libs
from core_libs import *

def get_name():
    return "ANSYS 4-PB Batch (Element Constraints)"


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
                        'obname': 'ffdir',
                        'placeholder': 'FEM File Directory Path',
                        'text': var_ins.fname,
                        'slots': {
                            'valueChanged': (
                                'working_dir', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'working_dir')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'working_dir', 'ffdir', QApplication.instance().main_window)
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
                        'type': 'QDoubleSpinBox',
                        'min': 0,
                        'max': 100000,
                        'value': var_ins.F,
                        'step': 1,
                        'dp': 2,
                        'slots': {
                            'valueChanged': (
                                'F', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'F')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Angle Increment (deg):'
                    },
                    {
                        'type': 'QDoubleSpinBox',
                        'min': 0,
                        'max': 360,
                        'value': var_ins.angle_inc,
                        'step': 10,
                        'dp': 2,
                        'slots': {
                            'valueChanged': (
                                'angle_inc', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'angle_inc')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Percentage of Remaining Segment:'
                    },
                    {
                        'type': 'QDoubleSpinBox',
                        'min': 0,
                        'max': 1,
                        'value': var_ins.pc,
                        'step': 0.05,
                        'dp': 2,
                        'slots': {
                            'valueChanged': (
                                'pc', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'pc')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Proportion of mid-segment to apply force:'
                    },
                    {
                        'type': 'QDoubleSpinBox',
                        'min': 0,
                        'max': 1,
                        'value': var_ins.pf,
                        'step': 0.05,
                        'dp': 2,
                        'slots': {
                            'valueChanged': (
                                'pf', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'pf')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QPushButton',
                'text': 'FEM Analysis',
                'slots': {
                    'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(batch_runner, gui_ins.core_count)
                }
            }
        ]
    }
    return gui_structure

def terminate_apdl():
    """Terminate any running APDL processes."""
    for proc in psutil.process_iter(['pid', 'name']):
        if 'ansys' in proc.info['name'].lower():
            proc.terminate()
            proc.wait()

def batch_runner():
    base_dir = var_ins.working_dir
    glob_pattern = os.path.join(base_dir, '**', '*.cdb')

    cdb_files = glob.glob(glob_pattern, recursive=True)
    print(cdb_files)

    for cdb_file in cdb_files:
        try:
            print(f"Processing: {cdb_file}")
            terminate_apdl()

            # print(cdb_file)

            file_name = os.path.basename(cdb_file)
            file_name_no_ext = os.path.splitext(file_name)[0]
            file_path = os.path.dirname(cdb_file)
            folder_name = os.path.basename(file_path)
            save_folder = f"results_{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"

            # print(f"File Name: {file_name}\nFile Name no ext: {file_name_no_ext}\nFile Path: {file_path}\nFolder Name: {folder_name}")

            var_ins.working_dir = file_path
            var_ins.id = file_name_no_ext

            # print(f"File Name: {file_name}\nFile Name no ext: {file_name_no_ext}\nFile Path: {file_path}\nFolder Name: {folder_name}")

            gui_ins.save_path = os.path.join(var_ins.working_dir, save_folder)
            os.makedirs(gui_ins.save_path, exist_ok=True)
            # print(f"Save path: {gui_ins.save_path}")

            bending()

        except Exception as e:
            print(f"[ERROR] Skipped {cdb_file} due to error: {e}")
            traceback.print_exc()

        finally:
            terminate_apdl()
            pass