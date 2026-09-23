"""
================================================================================================================
Post-Processing Library for ANSYS SideFall Results
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
import ansys.dpf.core.plotter
import numpy as np
import glob
import re
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
    return "ANSYS Sidefall Contour Results"


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


def ansys_pc_estrain():
    print("Creating ANSYS Plots...")

    # Get all rst files in the working directory
    rst_files = glob.glob(f"{var_ins.working_dir}/*.rst")

    # Filter out files with the pattern #_#.rst where # is a number
    filtered_rst_files = [f for f in rst_files if not re.search(r'.*\d+_\d+\.rst$', f)]
    print(filtered_rst_files)

    var_ins.output_dir = core_libs.gui_funcs.dir_check_and_make("post processed results", gui_ins.save_path)

    # window_size = [4000, 4000]
    window_size = [800, 800]
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


    cmap = ["#0000ff", "#00b3ff", "#00ffff", "#00ffb3", "#00ff00", "#b3ff00", "#ffff00", "#ffb300", "#ff0000"]

    for rst_file in filtered_rst_files:
        file_name = os.path.splitext(os.path.basename(rst_file))[0]
        try:
            solution = post.load_solution(rst_file)
            print("Result File Loaded")
            strain = solution.elastic_strain()
            data_sources = ansys.dpf.core.DataSources()
            data_sources.set_result_file_path(rst_file)
            data_sources.result_files.append(rst_file)
            model = ansys.dpf.core.Model(data_sources)
            fixed_zx_cpos = model.plot(return_cpos=True, cpos="zx", off_screen=True, screenshot=f'{var_ins.output_dir}/{file_name}_mesh.png',)
            fixed_zx_cpos = [
                fixed_zx_cpos[0],
                fixed_zx_cpos[1],
                (0.0, 0.0, 1.0)
            ]

            strain.principal_1.plot_contour(
                show_edges=True,
                clim=[0, 0.01],
                cpos="xy",
                cmap=cmap,
                below_color='blue',
                above_color='red',
                off_screen=True,
                window_size=window_size,
                screenshot=f'{var_ins.output_dir}/{file_name}_zy_1ps.png',
                scalar_bar_args=scalar_kwargs
            )

            strain.principal_1.plot_contour(
                show_edges=True,
                clim=[0, 0.01],
                cpos="xz",
                cmap=cmap,
                below_color='blue',
                above_color='red',
                off_screen=True,
                window_size=window_size,
                screenshot=f'{var_ins.output_dir}/{file_name}_xz_1ps.png',
                scalar_bar_args=scalar_kwargs
            )

            strain.principal_1.plot_contour(
                show_edges=True,
                clim=[0, 0.01],
                cpos="yz",
                cmap=cmap,
                below_color='blue',
                above_color='red',
                off_screen=True,
                window_size=window_size,
                screenshot=f'{var_ins.output_dir}/{file_name}_yz_1ps.png',
                scalar_bar_args=scalar_kwargs
            )

            strain.principal_1.plot_contour(
                return_cpos=True,
                show_edges=True,
                clim=[0, 0.01],
                cpos=fixed_zx_cpos,
                cmap=cmap,
                below_color='blue',
                above_color='red',
                off_screen=True,
                window_size=window_size,
                screenshot=f'{var_ins.output_dir}/{file_name}_zx_1ps.png',
                scalar_bar_args=scalar_kwargs
            )

            strain.principal_1.plot_contour(
                show_edges=True,
                clim=[0, 0.01],
                cpos="zy",
                cmap=cmap,
                below_color='blue',
                above_color='red',
                off_screen=True,
                window_size=window_size,
                screenshot=f'{var_ins.output_dir}/{file_name}_zy_1ps.png',
                scalar_bar_args=scalar_kwargs
            )

        except Exception as e:
            print(f"Error: Please ensure there is a *.rst file in {var_ins.working_dir} \n {e}")

    print(f"Plot Images Saved as *.png in {var_ins.output_dir}")
