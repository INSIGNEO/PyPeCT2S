"""
================================================================================================================
Post-Processing Library for ANSYS Bending Results
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
    return "ANSYS Bending Results"


def gui_elements():
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
                'type': 'QHBoxLayout',
                'items': [
                    {
                        'type': 'QPushButton',
                        'text': 'Numerical Results Processing',
                        'slots': {
                            'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(result_max_csv, gui_ins.core_count)
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'ANSYS Contour Plots',
                        'slots': {
                            'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(ansys_pc_estrain, gui_ins.core_count)
                        }
                    }
                ]
            }
        ]
    }
    return gui_structure

def calculate_moment_to_failure(strain1, strain3, esl_tension, esl_compression):
    if var_ins.x_upper is None:
        x_upper = np.loadtxt(f"{var_ins.working_dir}/output/x_upper.txt")
    else:
        x_upper = var_ins.x_upper
    if var_ins.fx_upper is None:
        fx_upper = np.loadtxt(f"{var_ins.working_dir}/output/fx_upper.txt")
    else:
        fx_upper = var_ins.fx_upper

    max_e1_strain = np.max(strain1) / esl_tension
    max_e3_strain = -np.min(strain3) / esl_compression

    if max_e1_strain >= max_e3_strain:
        force_to_failure = var_ins.F * esl_tension / np.max(strain1)
        fail_type = "Tension"
        moment_to_failure = (- force_to_failure * fx_upper / 1000) + (force_to_failure * x_upper / 1000)
        return force_to_failure, moment_to_failure, fail_type
    else:
        force_to_failure = var_ins.F * esl_compression / -np.min(strain3)
        fail_type = "Compression"
        moment_to_failure = (- force_to_failure * fx_upper / 1000) + (force_to_failure * x_upper / 1000)
        return force_to_failure, moment_to_failure, fail_type


def plot_stress_strain(strain1, strain3, ang, esl_tension, esl_compression):
    t_mask = strain1 >= esl_tension
    c_mask = strain3 <= -esl_compression

    plt.figure(1)
    plt.plot(ang, strain1, 'o')
    plt.plot(ang, strain3, '+')
    plt.hlines(y=0.0073, xmin=min(ang), xmax=max(ang), color='k', linewidth=1)
    plt.hlines(y=-0.0104, xmin=min(ang), xmax=max(ang), color='k', linewidth=1)
    plt.ylim(-0.015, 0.015)
    plt.xlabel('Angle (degrees)')
    plt.ylabel('Principal Strain')
    plt.legend(['Tension', 'Compression'])
    plt.savefig(f"{var_ins.output_dir}/Stress_Strain_1.pdf", format="pdf")

    plt.figure(2)
    plt.bar(ang[t_mask], strain1[t_mask], color='b', width=3, label='Tension')
    plt.bar(ang[c_mask] + 4, strain3[c_mask], color='r', width=3, label='Compression')
    plt.hlines(y=0.0073, xmin=min(ang), xmax=max(ang), color='k', linewidth=1)
    plt.hlines(y=-0.0104, xmin=min(ang), xmax=max(ang), color='k', linewidth=1)
    plt.ylim(-0.015, 0.015)
    plt.xlabel('Angle (degrees)')
    plt.ylabel('Failure Strain')
    plt.legend()
    plt.savefig(f"{var_ins.output_dir}/Stress_Strain_2.pdf", format="pdf")


def ansys_pc_estrain():
    print("Creating ANSYS Plots...")

    var_ins.output_dir = core_libs.gui_funcs.dir_check_and_make("post processed results", gui_ins.save_path)

    window_size = [4000, 4000]

    scalar_kwargs = {
        'title_font_size': int((8 / 400) * (window_size[0])),
        'label_font_size': int((6 / 400) * (window_size[0])),
        'shadow': False,
        'vertical': False,
        'n_labels': 6,
        'italic': True,
        'bold': True,
        'fmt': "%.4f",
        'font_family': "arial",
        'title': "1st - Principal Strain",
        'color': "black",
    }

    lateral_cpos = [(-112.97, 55.79, -245.12), (-40.11, 1.40, -199.23), (0.69, 0.42, -0.60)]
    medial_cpos = [(17.59, -55.58, -137.63), (-40.11, 1.40, -199.23), (-0.82, -0.30, 0.49)]

    cmap = ["#0000ff", "#00b3ff", "#00ffff", "#00ffb3", "#00ff00", "#b3ff00", "#ffff00", "#ffb300", "#ff0000"]

    try:
        solution = post.load_solution(f"{var_ins.working_dir}/file.rst")
        print("Result File Loaded")
        strain = solution.elastic_strain()

        strain.principal_1.plot_contour(
            show_edges=True,
            cpos=lateral_cpos,
            clim=[0, 0.01],
            cmap=cmap,
            below_color='blue',
            above_color='red',
            off_screen=True,
            window_size=window_size,
            screenshot=f'{var_ins.output_dir}/lateral_1ps.png',
            scalar_bar_args=scalar_kwargs
        )

        strain.principal_1.plot_contour(
            show_edges=True,
            cpos=medial_cpos,
            clim=[0, 0.01],
            cmap=cmap,
            below_color='blue',
            above_color='red',
            off_screen=True,
            window_size=window_size,
            screenshot=f'{var_ins.output_dir}/medial_1ps.png',
            scalar_bar_args=scalar_kwargs
        )

    except Exception as e:
        print(f"Error: Please ensure there is a *.rst file in {var_ins.working_dir} \n {e}")

    print(f"Plot Images Saved as *.png in {var_ins.output_dir}")


def result_max_csv():
    print("Compiling Strain Data...")

    var_ins.output_dir = core_libs.gui_funcs.dir_check_and_make("post processed results", gui_ins.save_path)
    res_dir = os.path.join(var_ins.working_dir, 'output')

    esl_tension = 0.0073  # 0.73% in tension | Elastic strain Limit Tension
    esl_compression = 0.0104  # 1.04% in compression | Elastic strain Limit Tension

    stress_files = [f for f in os.listdir(res_dir) if f.startswith("pstress") and f.endswith(".dat")]
    print(f"Found {len(stress_files)} Stress Files")
    # Sort the list of stress files in ascending order of angle
    stress_files.sort(key=lambda f: int(f.replace('pstress', '').split('.')[0]))

    for stress_file in stress_files:
        # if stress_file.startswith("pstress") and stress_file.endswith(".dat"):
        strain_file = "pstrain" + stress_file[7:]
        stress_file_path = os.path.join(res_dir, stress_file)
        strain_file_path = os.path.join(res_dir, strain_file)

        # Load data from stress and strain files, skipping the first line
        stress_data = np.loadtxt(stress_file_path, skiprows=1)
        strain_data = np.loadtxt(strain_file_path, skiprows=1)

        stress = stress_data[:, 1]  # 1 - 1st principal stress, 2 - 3rd principal stress
        strain1 = strain_data[:, 1]  # 1 - 1st principal strain, 2 - 3rd principal strain
        strain3 = strain_data[:, 2]  # 1 - 1st principal strain, 2 - 3rd principal strain

        # Calculate force and moment to failure
        try:
            force, moment, fail = calculate_moment_to_failure(strain1, strain3, esl_tension, esl_compression)
        except Exception as e:
            print(f"Error: {e}")
            force, moment, fail = None, None, None

        if force is not None and moment is not None:
            var_ins.force_to_failure.append(force)
            var_ins.moment_to_failure.append(moment)
            var_ins.data = np.append(
                var_ins.data,
                np.array(
                    [
                        (
                            int((stress_file.split('.')[0]).replace('pstress', '')),
                            np.max(strain1), (strain_data[:, 0][np.argmax(strain1)]),
                            np.min(strain3), (strain_data[:, 0][np.argmin(strain3)]),
                            fail,
                            force,
                            moment
                        )
                    ],
                    dtype=var_ins.dt
                )
            )

    # Plot stress-strain distribution
    plot_stress_strain(var_ins.data['Max Tension'], var_ins.data['Max Compression'], var_ins.data['Angle'], esl_tension, esl_compression)

    # plt.show()
    print(f"Average Force to Failure: {np.mean(var_ins.force_to_failure)} N")
    print(f"Average Moment to Failure: {np.mean(var_ins.moment_to_failure)} Nm")
    np.savetxt(
        f"{var_ins.output_dir}/Max_Strain_Bending.csv",
        var_ins.data,
        delimiter=",",
        fmt="%s",
        header='Angle,Max Tension,Node,Max Compression,Node,Fail Type,Force to Failure (N),Moment to Failure (Nm)',
        comments=''
    )
    print(f"Data Saved to CSV in {var_ins.output_dir}")
