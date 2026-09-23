"""
================================================================================================================
Post-Processing Library for ANSYS Sidefall Results
================================================================================================================
    Created by G.H. Allison, University of Sheffield, Sheffield, United Kingdom.
    Copyright (C) 2025 George H. Allison
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

import numpy as np
import matplotlib.pyplot as plt
from ansys.dpf import post
import os
from PyQt6.QtWidgets import QApplication
import core_libs
from core_libs import *

# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'cdb FEM Files (*.cdb);;DB FEM Files (*.db);;All Files (*)', 'ffdir', QApplication.instance().main_window) # for browse_file_path
# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'ffdir', QApplication.instance().main_window) # for browse_dir_path
var_ins = core_libs.ansys_vars.PostVariables()
gui_ins = core_libs.gui_vars.GuiVariables()


np.set_printoptions(precision=4, floatmode='fixed')


def get_name():
    return "ANSYS Sidefall Results"


def gui_elements():
    if not hasattr(var_ins, 'mat_threshold'):
        var_ins.mat_threshold = 0.0
    gui_structure = {
        'type': 'QVBoxLayout',  # Top-level layout
        'items': [
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Result File Directory:'
                    },
                    {
                        'type': 'QLineEdit',
                        'obname': 'resdir',
                        'placeholder': 'Result File Directory Path',
                        'text': var_ins.working_dir,
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
                                lambda: core_libs.gui_funcs.browse_dir_path('Select Result File Directory', var_ins, 'working_dir', 'resdir', QApplication.instance().main_window)
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
                'type': 'QHBoxLayout',
                'items': [
                    {'type': 'QLabel', 'text': 'Min Property Threshold (>=):'},
                    {
                        'type': 'QDoubleSpinBox',
                        'min': -1e12,
                        'max': 1e12,
                        'value': var_ins.mat_threshold,
                        'step': 0.001,
                        'dp': 4,
                        'slots': {
                            'valueChanged': (
                                'mat_threshold', var_ins,
                                lambda v: core_libs.gui_funcs.on_value_changed(v, var_ins, 'mat_threshold')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',
                'items': [
                    {
                        'type': 'QPushButton',
                        'text': 'Numerical Results Processing',
                        'slots': {
                            'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(result_max_csv, gui_ins.core_count)
                        }
                    }
                ]
            }
        ]
    }
    return gui_structure

def calculate_moment_to_failure(strain1, strain3, esl_tension, esl_compression):
    max_e1_strain = np.max(strain1) / esl_tension
    max_e3_strain = -np.min(strain3) / esl_compression

    if max_e1_strain >= max_e3_strain:
        force_to_failure = var_ins.F * esl_tension / np.max(strain1)
        fail_type = "Tension"
        return force_to_failure, fail_type
    else:
        force_to_failure = var_ins.F * esl_compression / -np.min(strain3)
        fail_type = "Compression"
        return force_to_failure, fail_type

def result_max_csv():
    print("Compiling Strain Data...")

    if not hasattr(var_ins, 'mat_threshold'):
        var_ins.mat_threshold = 0.0

    var_ins.force_to_failure = []
    var_ins.moment_to_failure = []
    var_ins.data = np.array([], dtype=var_ins.dt)

    var_ins.output_dir = core_libs.gui_funcs.dir_check_and_make("post processed results", gui_ins.save_path)
    res_dir = os.path.join(var_ins.working_dir)

    esl_tension = 0.0073  # 0.73% in tension | Elastic strain Limit Tension
    esl_compression = 0.0104  # 1.04% in compression | Elastic strain Limit Tension

    # Fixed strain limits for fallback filter
    e1_min, e1_max = 0.0, 0.01
    e3_min, e3_max = -0.01, 0.0

    e1_strain_files = [f for f in os.listdir(res_dir) if f.startswith("e1") and f.endswith(".dat")]
    e3_strain_files = [f for f in os.listdir(res_dir) if f.startswith("e3") and f.endswith(".dat")]

    for strain_file in e1_strain_files:
        angle = strain_file.split('.')[0].replace('e1', '')
        strain_file_path = os.path.join(res_dir, strain_file)
        strain_data = np.loadtxt(strain_file_path)
        # Merge strain data from e1 and e3 files
        if strain_file.startswith("e1") and strain_file.endswith(".dat"):
            strain3_file = "e3" + strain_file[2:]
            strain3_file_path = os.path.join(res_dir, strain3_file)
            strain3_data = np.loadtxt(strain3_file_path)

        roi_file = f"ROI_{angle}"
        roi_file_path = os.path.join(res_dir, roi_file + ".csv")
        if os.path.isfile(roi_file_path):
            with open(roi_file_path, "r") as roi_file:
                node_lines = [line.strip() for line in roi_file.readlines()]
        else:
            node_lines = [''] * len(strain_data)    # Ensure node_lines matches strain_data length
        strain1 = strain_data[:]
        strain3 = strain3_data[:] if 'strain3_data' in locals() else None

        mask = np.ones_like(strain1, dtype=bool)
        range_mask = (
                (strain1 >= e1_min) & (strain1 <= e1_max) &
                (strain3 >= e3_min) & (strain3 <= e3_max)
        )
        mask = range_mask

        if mask.sum() == 0:
            print(f"Info: no nodes pass filter for angle {angle}, skipping.")
            continue

        f_strain1 = strain1[mask]
        f_strain3 = strain3[mask]
        f_nodes = [node_lines[i] for i, m in enumerate(mask) if m]

        # Calculate force and moment to failure
        force, fail = None, None
        try:
            force, fail = calculate_moment_to_failure(f_strain1, f_strain3, esl_tension, esl_compression)
        except Exception as e:
            print(f"Error: {e}")
            force, fail = None, None

        if force is not None:
            max_tension_node = np.argmax(f_strain1)
            max_compression_node = np.argmin(f_strain3)
            var_ins.force_to_failure.append(force)
            var_ins.data = np.append(
                var_ins.data,
                np.array(
                    [
                        (
                            strain_file.split('.')[0].replace('e1', ''),
                            np.max(f_strain1), node_lines[max_tension_node] if max_tension_node < len(node_lines) else '',
                            np.min(f_strain3), node_lines[max_compression_node] if max_compression_node < len(node_lines) else '',
                            fail,
                            force,
                            np.nan
                        )
                    ],
                    dtype=np.dtype([('Angle', 'U11'), ('Max Tension', float), ('Tension Node', int),
                                ('Max Compression', float), ('Compression Node', int), ('Fail Type', 'U11'),
                                ('Force to Fail', float), ('Moment to Fail', float)])
                )
            )

    # plt.show()

    # the data is not in an proper array, it is 1 column of data and rows of data so harder to delete columns
    np.savetxt(
        f"{var_ins.output_dir}/Max_Strain_Bending.csv",
        var_ins.data,
        delimiter=",",
        fmt="%s",
        header='Angle,Max Tension,Node,Max Compression,Node,Fail Type,Force to Failure (N)',
        comments=''
    )
    print(f"Data Saved to CSV in {var_ins.output_dir}")

    # Extract the lowest force and write summary
    if len(var_ins.data) > 0:
        min_force_idx = np.argmin(var_ins.data['Force to Fail'])
        min_row = var_ins.data[min_force_idx]
        match min_row['Angle']:
            case str(x) if 'lat' in x:
                position = 'Lateral'
            case str(x) if 'med' in x:
                position = 'Medial'
            case str(x) if 'post' in x:
                position = 'Posterior'
            case str(x) if 'ant' in x:
                position = 'Anterior'
            case str(x) if 'neut' in x:
                position = 'Neutral'
            case _:
                position = min_row['Angle']
        angle_str = str(min_row['Angle'])
        numeric_chars = ''.join([char for char in angle_str  if char.isdigit()])
        angle = int(numeric_chars) if numeric_chars else 0
        fail_type = min_row['Fail Type']
        force_val = min_row['Force to Fail']
        summary = f"Bone failed at {position} position at angle {angle}, failing in {fail_type} at a force of {force_val:.2f} N"
        with open(f"{var_ins.output_dir}/failure_summary.txt", "w") as f:
            f.write(summary)

    print(f"Average Force to Failure: {np.mean(var_ins.force_to_failure)} N")
    print(summary)