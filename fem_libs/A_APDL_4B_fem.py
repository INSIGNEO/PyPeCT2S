"""
================================================================================================================
Python script to automate 4-point bending analysis in ANSYS APDL as part of the CT2S pipeline
================================================================================================================
    Created by G.H. Allison, University of Sheffield, Sheffield, United Kingdom.
    Initial creation date: 28-November-2023.
    Current version date: 29-July-2024
    Based on prior work by Dr. Xinshan Li and Dr. Zainab Altai.
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
import numpy as np
import glob
from ansys.mapdl.core import launch_mapdl
from PyQt6.QtWidgets import QApplication
import core_libs
from core_libs import *

# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'cdb FEM Files (*.cdb);;DB FEM Files (*.db);;All Files (*)', 'ffdir', QApplication.instance().main_window) # for browse_file_path
# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'ffdir', QApplication.instance().main_window) # for browse_dir_path
var_ins = core_libs.ansys_vars.FemVariables()
gui_ins = core_libs.gui_vars.GuiVariables()


def get_name():
    return "ANSYS 4 Point Bending"


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
                        'text': 'Filename:'
                    },
                    {
                        'type': 'QLineEdit',
                        'placeholder': 'FEM File Name',
                        'slots': {
                            'valueChanged': (
                                'id', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'id')
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
                        'text': 'Manual:'
                    },
                    {
                        'type': 'QSpinBox',
                        'min': 1,
                        'max': 2,
                        'value': var_ins.manual,
                        'step': 1,
                        'slots': {
                            'valueChanged': (
                                'manual', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'manual')
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
                    'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(bending, gui_ins.core_count)
                }
            }
        ]
    }
    return gui_structure


def local_func(mapdl):
    """
    This function creates a local coordinate system for the femur.
    The femur is re-aligned along the mid-shaft by defining another local coordinate system.
    The simulation is then run for each orientation.
    These local coordinates differ only in the +y dir.
    """

    sys = 11  # index of first local coordinate system, starting at 11m, where the femur is re-aligned along the mid-shaft
    var_ins.csys_num[0] = 12  # Second defined local coordinate system, where x-axis is aligned to pass through mid of the cross-section
    var_ins.kp_num[0] = 3  # index of first proximal kp
    var_ins.rad[0] = 0  # initial angle of rotation in radians
    var_ins.angle[0] = 0  # initial angle of rotation in degrees

    mapdl.prep7()  # Enters pre-processing mode

    # Create first local coordinate system. Define three key points for local coordinate system.
    mapdl.k(1, var_ins.middle[0], var_ins.middle[1], var_ins.middle[2])  # Origin - mid-shaft
    mapdl.k(2, var_ins.distal[0], var_ins.distal[1], var_ins.distal[2])  # Positive x
    mapdl.k(var_ins.kp_num[0], var_ins.proximal[0], var_ins.proximal[1], var_ins.proximal[2])  # Positive y

    # Define local coordinate system.
    mapdl.cskp(11, 0, 1, 2, 3)  # Create local coordinate system 11, origin at kp 1, x-axis at kp 2, y-axis at kp 3

    # Rotates nodes and key points to coincide with new local coordinate system.
    mapdl.dsys(11)  # Sets local coordinate system as the active coordinate system.
    mapdl.nrotat("all")  # Rotates all nodes to coincide with local coordinate system.

    """
    ================================================================================================================
    New coordinate system aligned through the mid-shaft section
    ================================================================================================================
    """

    # Find the max and min node in the x direction along the shaft.
    x1_max = mapdl.get_value("node", "", "MXLOC", "x")
    x1_min = mapdl.get_value("node", "", "MNLOC", "x")
    l1 = x1_max - x1_min  # Length of the shaft in the x direction
    # Use origin as the mid-point of the resulting segment.
    x1_upper = l1 * var_ins.pc / 2  # Upper bound of the segment
    x1_lower = -l1 * var_ins.pc / 2  # Lower bound of the segment
    # Find mid of proximal end

    mapdl.nsel("s", "loc", "x", x1_lower)  # Selects nodes within the lower segment
    mapdl.nsel("r", "ext")  # Selects external nodes
    mapdl.cm("Proximal", "node")  # Creates a component called Proximal

    xmin_proxend = mapdl.get_value("node", "", "MNLOC", "x")  # Finds the minimum x value of the proximal end

    ymax_proxend = mapdl.get_value("node", "", "MXLOC", "y")  # Finds the maximum y value of the proximal end
    ymin_proxend = mapdl.get_value("node", "", "MNLOC", "y")  # Finds the minimum y value of the proximal end

    zmax_proxend = mapdl.get_value("node", "", "MXLOC", "z")  # Finds the maximum z value of the proximal end
    zmin_proxend = mapdl.get_value("node", "", "MNLOC", "z")  # Finds the minimum z value of the proximal end

    xprox = xmin_proxend
    yprox = (ymax_proxend + ymin_proxend) / 2
    zprox = (zmax_proxend + zmin_proxend) / 2

    mapdl.allsel("all")  # Selects all nodes

    # Find mid of distal end

    mapdl.nsel("s", "loc", "x", x1_upper)  # Selects nodes within the upper segment
    mapdl.nsel("r", "ext")  # Selects external nodes
    mapdl.cm("distal", "node")  # Creates a component called Distal

    xmin_distend = mapdl.get_value("node", "", "MNLOC", "x")  # Finds the minimum x value of the distal end

    ymax_distend = mapdl.get_value("node", "", "MXLOC", "y")  # Finds the maximum y value of the distal end
    ymin_distend = mapdl.get_value("node", "", "MNLOC", "y")  # Finds the minimum y value of the distal end

    zmax_distend = mapdl.get_value("node", "", "MXLOC", "z")  # Finds the maximum z value of the distal end
    zmin_distend = mapdl.get_value("node", "", "MNLOC", "z")  # Finds the minimum z value of the distal end

    xdistal = xmin_distend
    ydistal = (ymax_distend + ymin_distend) / 2
    zdistal = (zmax_distend + zmin_distend) / 2

    mapdl.allsel("all")  # Selects all nodes

    # Find the new origin of the local coordinate system

    xmid = (xprox + xdistal) / 2
    ymid = (yprox + ydistal) / 2
    zmid = (zprox + zdistal) / 2

    mapdl.get("Max_kp", "kp", "", "num", "max")  # Finds the maximum kp number

    kp1 = 40
    kp2 = 41

    # Create new coordinate system aligned with centre of the two ends.
    mapdl.k(kp1, xmid, ymid, zmid)  # Origin - mid-point of the segment
    mapdl.k(kp2, xdistal, ydistal, zdistal)  # Positive x

    mapdl.cskp(var_ins.csys_num[0], 0, kp1, kp2, "3")  # Create local coordinate system 12, origin at kp 40, x-axis at kp 41, y-axis at kp 3

    mapdl.csys(12)
    mapdl.dsys(12)  # Sets local coordinate system as the active coordinate system.
    mapdl.nsel("all")  # Selects all nodes
    mapdl.nrotat("all")  # Rotates all nodes to coincide with local coordinate system.

    """
    ================================================================================================================
    Update key points
    ================================================================================================================
    Obtains the updated coord for the proximal key point, 
    the first value (x) provides the origin of the rotation,
    the second value (y) provides the radius of the rotation.
    """

    var_ins.px_rot = mapdl.get_value("kp", "3", "loc", "x")  # Finds the x value of the proximal key point
    var_ins.py_rot[0] = mapdl.get_value("kp", "3", "loc", "y")  # Finds the y value of the proximal key point
    var_ins.pz_rot[0] = mapdl.get_value("kp", "3", "loc", "z")  # Finds the z value of the proximal key point

    r = var_ins.py_rot[0]  # Radius of rotation

    # Final setup, loop through the number of steps if additional local coordinate systems are required.

    if var_ins.mode == 1:
        if var_ins.step > 1:
            for i in range(1, var_ins.step, 1):
                var_ins.rad[i] = var_ins.rad[0] + var_ins.rad_inc * (i)
                var_ins.angle[i] = var_ins.angle[0] + var_ins.angle_inc * (i)
                var_ins.py_rot[i] = r * np.cos(var_ins.rad[i])
                var_ins.pz_rot[i] = r * np.sin(var_ins.rad[i])

                # Redifine third key point.
                var_ins.kp_num[i] = var_ins.kp_num[i - 1] + 1
                mapdl.k(var_ins.kp_num[i], var_ins.px_rot, var_ins.py_rot[i], var_ins.pz_rot[i])  # Positive y

                # Define local coordinate system.
                # Defined using kp coordinates in csys 11.
                var_ins.csys_num[i] = var_ins.csys_num[i - 1] + 1
                mapdl.cskp(var_ins.csys_num[i], 0, kp1, kp2, var_ins.kp_num[i])

                mapdl.csys(12)
                mapdl.dsys(12)
                mapdl.nrotat("all")
            print("csys_nums logged")

        else:
            print("Only one step required")
    else:
        print("Torsion selected")

    # Export angle data
    with open((os.path.join(var_ins.output_dir, 'angle.dat')), 'w') as f:
        f.write("csys   Radian    Angle  kp   pxX   pxY   pxZ\n")
        for i in range(len(var_ins.csys_num)):
            f.write(
                f"{var_ins.csys_num[i]:6.0f} {var_ins.rad[i]:6.2f} {var_ins.angle[i]:6.1f} {var_ins.kp_num[i]:6.0f} {var_ins.px_rot:10.0f} {var_ins.py_rot[i]:10.6f} {var_ins.pz_rot[i]:10.6f}\n")

    mapdl.finish()


def init_func(value, mapdl):
    """
    This function initialises the model for simulation.
    """

    print("starting initialisation function")

    mapdl.prep7()  # Enters pre-processing mode

    mapdl.csys(var_ins.csys_num[value])  # Sets a local coordinate system as the active coordinate system.
    mapdl.dsys(var_ins.csys_num[value])  # displays a local coordinate system as the active coordinate system.
    mapdl.nrotat("all")  # Rotates all nodes to coincide with local coordinate system.
    mapdl.allsel("all")  # Selects all nodes

    # Crop the bone and keep the mid-shaft section
    if value == 0:
        x_max = mapdl.get_value("node", "", "MXLOC", "x")  # Finds the maximum x value of the bone
        x_min = mapdl.get_value("node", "", "MNLOC", "x")  # Finds the minimum x value of the bone

        l = x_max - x_min  # Length of the bone in the x direction

        # Use origin as the mid-point of the resulting segment.
        var_ins.x_upper = l * var_ins.pc / 2  # Upper bound of the segment
        var_ins.x_lower = -l * var_ins.pc / 2  # Lower bound of the segment

        # For applying force
        l_seg = var_ins.x_upper - var_ins.x_lower  # Length of the segment in the x direction
        var_ins.fx_upper = l_seg * var_ins.pf / 2  # Upper bound of the segment
        var_ins.fx_lower = -l_seg * var_ins.pf / 2  # Lower bound of the segment

        print(f"x_upper: {var_ins.x_upper}")
        print(f"fx_upper: {var_ins.fx_upper}")
        np.savetxt(f"{var_ins.output_dir}/x_upper.txt", [var_ins.x_upper], fmt='%.10f')
        np.savetxt(f"{var_ins.output_dir}/fx_upper.txt", [var_ins.fx_upper], fmt='%.10f')

        # Select the distal and proximal ends of the bone to be removed.
        mapdl.esel("s", "cent", "x", var_ins.x_upper, x_max + 3)  # Selects elements within the lower segment
        mapdl.edele("all")  # Deletes selected elements
        mapdl.ndele("all")  # Deletes selected nodes

        mapdl.esel("s", "cent", "x", var_ins.x_lower, x_min - 3)  # Selects elements within the lower segment
        mapdl.edele("all")  # Deletes selected elements
        mapdl.ndele("all")  # Deletes selected nodes

        mapdl.allsel("all")  # Selects all nodes

    mapdl.finish()  # Exits pre-processing mode

    # Boundary constraints

    mapdl.slashsolu()  # Enters solution mode

    # Delete previous displacement constraints
    if value > 0:
        mapdl.ddele("all")  # Deletes all displacement constraints

    # Fix the nodes of the bone
    # Bending
    if var_ins.mode == 1:
        mapdl.nsel("s", "loc", "x", var_ins.x_upper)  # Selects nodes within the upper segment
        mapdl.nsel("r", "ext")  # Selects external nodes

        # Fix bottom node in all directions - from XSL 30-September-2013
        y_min_upper = mapdl.get_value("node", "", "MNLOC", "y")  # Finds the minimum y value of the upper segment
        mapdl.nsel("r", "loc", "y", y_min_upper, y_min_upper + 0.05)  # Selects nodes within the upper segment
        mapdl.d("all", "all", 0)  # Fixes all degrees of freedom for selected nodes

        mapdl.allsel("all")  # Selects all nodes

        if var_ins.id != 'PM7':  # PM7 has kinky elements at the end with standard command.
            mapdl.nsel("s", "loc", "x", var_ins.x_lower)  # Selects nodes within the lower segment
            mapdl.nsel("r", "ext")  # Selects external nodes
        else:
            mapdl.nsel("s", "loc", "x", var_ins.x_lower + 0.3)  # Selects nodes within the lower segment
            mapdl.nsel("r", "ext")  # Selects external nodes

        # Fix in y in lower x segment - XSL 30-September-2013
        y_min_lower = mapdl.get_value("node", "", "MNLOC", "y")  # Finds the minimum y value of the lower segment
        mapdl.nsel("r", "loc", "y", y_min_lower, y_min_lower)  # Selects nodes within the lower segment
        mapdl.d("all", "uy", 0)  # Fixes all degrees of freedom for selected nodes

        mapdl.allsel("all")  # Selects all nodes

        # Fix in z in lower x segment - XSL 04-October-2013
        mapdl.nsel("s", "loc", "x", var_ins.x_lower)  # Selects nodes within the lower segment
        mapdl.nsel("r", "ext")  # Selects external nodes
        z_min_lower = mapdl.get_value("node", "", "MNLOC", "z")  # Finds the minimum z value of the lower segment
        mapdl.nsel("r", "loc", "z", z_min_lower)  # Selects nodes within the lower segment
        mapdl.d("all", "uz", 0)  # Fixes all degrees of freedom for selected nodes

        mapdl.allsel("all")  # Selects all nodes

        # Fix in z in upper x segment - XSL 07-October-2013
        mapdl.nsel("s", "loc", "x", var_ins.x_upper)  # Selects nodes within the lower segment
        mapdl.nsel("r", "ext")  # Selects external nodes
        z_min_upper = mapdl.get("z_min_upper", "node", "", "MNLOC",
                                "z")  # Finds the minimum z value of the lower segment
        mapdl.nsel("r", "loc", "z", z_min_upper)  # Selects nodes within the lower segment
        mapdl.d("all", "uz", 0)  # Fixes all degrees of freedom for sele

    mapdl.allsel("all")  # Selects all nodes

    # Apply force on top
    # Delete previous force constraints
    if value > 0:
        mapdl.fdele("all")

    # Bending
    if var_ins.mode == 1:
        # Upper x segment

        mapdl.nsel("s", "loc", "x", var_ins.fx_upper - 1, var_ins.fx_upper + 1)  # Selects nodes within the upper segment

        fy_max_upper = mapdl.get_value("node", "", "MXLOC", "y")  # Finds the maximum y value of the upper segment
        fy_min_upper = mapdl.get_value("node", "", "MNLOC", "y")  # Finds the minimum y value of the upper segment
        mapdl.nsel("r", "loc", "y", fy_max_upper - 0.5, fy_max_upper)  # Selects nodes within the upper segment
        mapdl.nsel("r", "ext")  # Selects external nodes

        # Store the node number
        fnodenum_upper = mapdl.get_value("node", "", "count")  # Finds the maximum node number of the upper segment

        # Approximate diameter for upper x segment
        d_upper = fy_max_upper - fy_min_upper  # Diameter of the upper segment

        # Set active coord back to global before applying force which will act in the local coord
        mapdl.csys(0)
        mapdl.dsys(0)
        if fnodenum_upper == 0:
            mapdl.f("all", "fy", "0")  # Apply force in the y direction to all nodes in the upper segment
        else:
            mapdl.f("all", "fy", -var_ins.F / fnodenum_upper)  # Apply force in the y direction to all nodes in the upper segment

        # Lower x segment
        mapdl.allsel("all")  # Selects all nodes

        mapdl.csys(var_ins.csys_num[value])  # Sets a local coordinate system as the active coordinate system.
        mapdl.dsys(var_ins.csys_num[value])  # displays a local coordinate system as the active coordinate system.

        mapdl.nsel("s", "loc", "x", var_ins.fx_lower - 1, var_ins.fx_lower + 1)  # Selects nodes within the lower segment
        fy_max_lower = mapdl.get_value("node", "", "MXLOC", "y")  # Finds the maximum y value of the lower segment
        fy_min_lower = mapdl.get_value("node", "", "MNLOC", "y")  # Finds the minimum y value of the lower segment
        mapdl.nsel("r", "loc", "y", fy_max_lower - 0.5, fy_max_lower)  # Selects nodes within the lower segment
        mapdl.nsel("r", "ext")  # Selects external nodes

        # Store the node number
        fnodenum_lower = mapdl.get_value("node", "", "count")

        # Approximate diameter for lower x segment
        d_lower = fy_max_lower - fy_min_lower  # Diameter of the lower segment

        # Set active coord back to global before applying force which will act in the local coord
        mapdl.csys(0)
        mapdl.dsys(0)
        if fnodenum_lower == 0:
            mapdl.f("all", "fy", "0")  # Apply force in the y direction to all nodes in the upper segment
        else:
            mapdl.f("all", "fy", -var_ins.F / fnodenum_lower)  # Apply force in the y direction to all nodes in the lower segment

    mapdl.allsel("all")  # Selects all nodes

    # Get external nodes in the region of interest
    if value == 0:
        # St Ventant Principle, the ROI should be one distance away from where loads are applied.

        mapdl.csys(var_ins.csys_num[value])  # Sets a local coordinate system as the active coordinate system.
        mapdl.dsys(var_ins.csys_num[value])  # displays a local coordinate system as the active coordinate system.

        max_node_number = mapdl.get("max_node_number", "node", "", "num", "maxd")  # Finds the maximum node number of the model
        mapdl.esel("s", "cent", "x", var_ins.fx_lower + d_lower, var_ins.fx_upper - d_upper)  # Selects elements within the ROI

        # Select corner nodes associated with these elements. This excludes mid-side nodes.
        # Because stress/strain results are not saved at those nodes. Hence, cannot get them in post-processing.
        mapdl.nsle("s", "corner")  # Selects nodes within the ROI
        mapdl.esel("all")  # Selects all elements
        mapdl.nsel("r", "ext")  # Selects external nodes

        var_ins.nodenum_roi = mapdl.get_value("node", "", "count")  # Finds the number of nodes in the ROI

        # Define array to save xyz of selected nodes in ROI
        var_ins.roi_x = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for x coordinates of ROI nodes
        var_ins.roi_y = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for y coordinates of ROI nodes
        var_ins.roi_z = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for z coordinates of ROI nodes
        var_ins.roi_node = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for node numbers of ROI nodes

        # Define array to save pstrain and pstress results in export function
        var_ins.pstrain1 = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for pstrain1 results of ROI nodes
        var_ins.pstrain3 = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for pstrain3 results of ROI nodes
        var_ins.pstress1 = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for pstress1 results of ROI nodes
        var_ins.pstress3 = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for pstress3 results of ROI nodes

        node_list_coords = mapdl.mesh.nodes_in_current_CS
        # print(f"node_list_coord:{node_list_coords} ,length: {len(node_list_coords)}")
        var_ins.roi_x = node_list_coords[:, 0]  # Assigns all rows of column 0 to roi_x
        var_ins.roi_y = node_list_coords[:, 1]  # Assigns all rows of column 1 to roi_y
        var_ins.roi_z = node_list_coords[:, 2]  # Assigns all rows of column 2 to roi_z

        var_ins.roi_node = mapdl.mesh.nnum  # Assigns all node numbers to roi_node
        print(f"{len(var_ins.roi_node)} - Nodes added to the ROI.\nWriting out node numbers.")

        # Write out total number of nodes and individual node numbers in ROI
        with open((os.path.join(var_ins.output_dir, 'roi.dat')), 'w') as f:
            f.write(f"{int(var_ins.nodenum_roi)}\n")
            for i in range(int(var_ins.nodenum_roi)):
                f.write(f"{int(var_ins.roi_node[i])}\n")

    # Reset to global coordinate system for solving

    mapdl.csys(0)
    mapdl.dsys(0)

    mapdl.allsel("all")  # Selects all nodes

    mapdl.finish()  # Exits solution mode

    print("Finished Initialisation Function")


def solve_func(value, mapdl):
    """
    This function solves the model. Ready for export
    """
    mapdl.slashsolu()  # Enters solution mode

    if var_ins.mode == 2:
        mapdl.nlgeom("on")  # Turns on non-linear geometry

    mapdl.eqslv("pcg", 1e-7)  # Sets the equation solver to PCG with a tolerance of 1e-7

    mapdl.solve()  # Solves the model

    var_ins.fname = int(var_ins.angle[value])

    mapdl.save(str(var_ins.id) + "_" + str(var_ins.fname), "db")  # Saves the model
    print("Saved Solve")


def export_func(value, mapdl):
    """
    This function outputs the principle stress and strain results for the ROI.
    """
    mapdl.post1()  # Enters post-processing mode

    mapdl.nsel("s", "node", "", var_ins.roi_node)  # Selects nodes within the ROI

    mapdl.post_processing.selected_nodes

    # Finds the principle strain in the x direction
    pstrain1 = mapdl.post_processing.nodal_elastic_principal_strain("1")
    # pstrain1 = [mapdl.get_value("node", node, "epel", "1") for node in roi_node]

    # Finds the principle strain in the z direction
    pstrain3 = mapdl.post_processing.nodal_elastic_principal_strain("3")
    # pstrain3 = [mapdl.get_value("node", node, "epel", "3") for node in roi_node]

    # Finds the principle stress in the x direction
    pstress1 = mapdl.post_processing.nodal_principal_stress("1")
    # pstress1 = [mapdl.get("pstress1", "node", node, "s", "1") for node in roi_node]

    # Finds the principle stress in the z direction
    pstress3 = mapdl.post_processing.nodal_principal_stress("3")
    # pstress3 = [mapdl.get_value("node", node, "s", "3") for node in roi_node]

    # Print the status
    var_ins.fname = int(var_ins.angle[value])

    # Export principle strain and stress results to file
    with open((os.path.join(var_ins.output_dir, f'pstrain{var_ins.fname}.dat')), 'w') as f:
        f.write("Node   Strain1   Strain3\n")
        for i in range(int(var_ins.nodenum_roi)):
            f.write(f"{var_ins.roi_node[i]:7.0f} {pstrain1[i]:10.6f} {pstrain3[i]:10.6f}\n")

    with open((os.path.join(var_ins.output_dir, f'pstress{var_ins.fname}.dat')), 'w') as f:
        f.write("Node   Stress1   Stress3\n")
        for i in range(int(var_ins.nodenum_roi)):
            f.write(f"{var_ins.roi_node[i]:7.0f} {pstress1[i]:10.6f} {pstress3[i]:10.6f}\n")

    print("Exported Results")


def bending():
    var_ins.output_dir = core_libs.gui_funcs.dir_check_and_make('output', gui_ins.save_path)  # Creates output directory

    landmarks_dir = os.path.join(var_ins.working_dir, 'landmarks')
    if os.path.exists(landmarks_dir) and os.listdir(landmarks_dir):
        # Read landmarks from files
        for file_name in os.listdir(landmarks_dir):
            file_path = os.path.join(landmarks_dir, file_name)
            core_libs.ldmk_funcs.read_landmark_file(file_path, var_ins)
        print(f"Landmarks read from files")
    else:
        # Run find_landmarks function
        core_libs.ldmk_funcs.find_landmarks(var_ins)
        print("Landmarks found using auto landmark function")

    mapdl = launch_mapdl(nproc=gui_ins.core_count, additional_switches='-smp', loglevel="WARNING", print_com=True,
                         cleanup_on_exit=True)
    mapdl.clear()
    file_path = glob.glob(f"{var_ins.working_dir}/{var_ins.id}*")[0].replace("\\", "/")
    file, file_extension = os.path.splitext(file_path)

    match file_extension.lower():
        case ".db":
            file = os.path.splitext(glob.glob(f'{var_ins.working_dir}/{var_ins.id}*')[0].replace("\\", "/"))[0]
            print(f"File: {file}")
            mapdl.resume(file, 'db', '', 0)  # Loads the *.db file for running ANSYS
        case ".cdb":
            file = os.path.splitext(glob.glob(f'{var_ins.working_dir}/{var_ins.id}*')[0].replace("\\", "/"))[0]
            print(f"File: {file}")
            mapdl.cdread('DB', file, 'cdb')  # Loads the *.cdb file for running ANSYS
        case _:
            print(f"Error: No file(s) found that called {var_ins.id} in {var_ins.working_dir}")

    mapdl.cwd(gui_ins.save_path)  # Changes working directory to save outputs and save temp files away from initial model

    if var_ins.mode == 1:
        if var_ins.manual != 1:
            var_ins.step = int(360 / var_ins.angle_inc)
        else:
            var_ins.step = 2
        var_ins.rad_inc = np.deg2rad(var_ins.angle_inc)
    else:
        n = 1  # index for variable csys_num, csys_num(1) = 11 local coordinates
        var_ins.step = 2
    print(f"Step: {var_ins.step}\nrad_inc: {var_ins.rad_inc}\n")

    var_ins.py_rot = np.zeros(var_ins.step)
    var_ins.pz_rot = np.zeros(var_ins.step)
    var_ins.rad = np.zeros(var_ins.step)
    var_ins.angle = np.zeros(var_ins.step)
    var_ins.csys_num = np.zeros(var_ins.step)
    var_ins.kp_num = np.zeros(var_ins.step)

    local_func(mapdl)
    print("Local function complete")

    if var_ins.export_EX == 1:
        print('fill in later')
        # Call exmid_export script
    else:
        for i in range(var_ins.step):
            print(f"Running loop {i}")
            init_func(i, mapdl)
            if var_ins.manual != 1:
                solve_func(i, mapdl)
                export_func(i, mapdl)
                print(f"Loop {i} complete")
            else:
                print("can't solve or export")
        print("All loops complete")

    mapdl.finish()
    mapdl.exit()
