"""
================================================================================================================
Python script to automate 4-point bending analysis in ANSYS APDL as part of the CT2S pipeline
================================================================================================================
    Created by G.H. Allison, University of Sheffield, Sheffield, United Kingdom.
    Initial creation date: 28-November-2023.
    Current version date: 03-November-2025
    Based on prior work by Dr. Xinshan Li and Dr. Zainab Altai.
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

import os
import numpy as np
import glob
from ansys.mapdl.core import launch_mapdl
from PyQt6.QtWidgets import QApplication
from fontTools.merge.layout import mapLookups
import traceback
import sys

import core_libs
from core_libs import *

# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'cdb FEM Files (*.cdb);;DB FEM Files (*.db);;All Files (*)', 'ffdir', QApplication.instance().main_window) # for browse_file_path
# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'ffdir', QApplication.instance().main_window) # for browse_dir_path
var_ins = core_libs.ansys_vars.FemVariables()
gui_ins = core_libs.gui_vars.GuiVariables()

def get_name():
    return "ANSYS Torsion"

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
                                'working_dir', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'working_dir')
                            )
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins,
                                                                            'working_dir', 'ffdir',
                                                                            QApplication.instance().main_window)
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
                                'id', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'id')
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
                        'text': 'Moment (Nm):'
                    },
                    {
                        'type': 'QDoubleSpinBox',
                        'min': 0,
                        'max': 100000,
                        'value': var_ins.M,
                        'step': 1,
                        'dp': 2,
                        'slots': {
                            'valueChanged': (
                                'M', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'M')
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
                        'text': 'Direction (internal/external):'
                    },
                    {
                        'type': 'QComboBox',
                        'placeholder': 'Select Direction',
                        'value': var_ins.direc,
                        'items': ['internal', 'external'],
                        'slots': {
                            'valueChanged': (
                                'direc', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'direc')
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
                        'text': 'Under One Year Old:'
                    },
                    {
                        'type': 'QCheckBox',
                        'text': 'Under One Year Old',
                        'value': var_ins.under_one_year,
                        'slots': {
                            'valueChanged': (
                                'under_one_year', var_ins,
                                lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'under_one_year')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QPushButton',
                'text': 'FEM Analysis',
                'slots': {
                    'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(torsion, gui_ins.core_count)
                }
            }
        ]
    }
    return gui_structure

def local_func(mapdl):
    """
    This function sets up the local coordinate systems and calculates the length of the femur.
    """
    p_x = (var_ins.distal[0] - var_ins.proximal[0]) * (var_ins.distal[0] - var_ins.proximal[0])
    p_y = (var_ins.distal[1] - var_ins.proximal[1]) * (var_ins.distal[1] - var_ins.proximal[1])
    p_z = (var_ins.distal[2] - var_ins.proximal[2]) * (var_ins.distal[2] - var_ins.proximal[2])
    l_femur = np.sqrt(p_x + p_y + p_z)

    # I don't like this calculation, it relies on assumtion of Schileo 2007 and a linear relationship with children
    max_elem_size = 3*l_femur/430

    var_ins.csys_num = 11  # Second defined local coordinate system, where x-axis is aligned to pass through mid of the cross-section

    mapdl.prep7()  # Enters pre-processing mode

    # Create first local coordinate system. Define three key points for local coordinate system.
    mapdl.k(1, var_ins.middle[0], var_ins.middle[1], var_ins.middle[2])  # Origin - mid-shaft
    mapdl.k(2, var_ins.distal[0], var_ins.distal[1], var_ins.distal[2])  # Positive x
    mapdl.k(3, var_ins.proximal[0], var_ins.proximal[1], var_ins.proximal[2])  # Positive y

    mapdl.cskp(var_ins.csys_num, 0, 1, 2, 3)  # Create local coordinate system

    mapdl.dsys(11)
    mapdl.nrotat("all")
    mapdl.allsel("all")

    roi_range = max_elem_size/2
    mapdl.nsle("S", "corner")
    mapdl.nsel("R", "LOC", "X", roi_range, -roi_range)
    mapdl.nsel("R", "ext")
    mapdl.cm("MidShaft_nodes", "NODE")

    mapdl.allsel("all")

    # Find the max and min node in the x direction along the shaft.
    x1_max = mapdl.get_value("node", "", "MXLOC", "x")
    x1_min = mapdl.get_value("node", "", "MNLOC", "x")
    var_ins.l = x1_max - x1_min  # Length of the shaft in the x direction
    # Use origin as the mid-point of the resulting segment.
    x1_upper = var_ins.l * var_ins.pc / 2  # Upper bound of the segment
    x1_lower = -var_ins.l * var_ins.pc / 2  # Lower bound of the segment

    mapdl.csys(11)
    mapdl.dsys(11)
    mapdl.allsel("all")

    """
    ================================================================================================================
    Create components of nodes on the two ends for MPC elements and align coordinate system through mid-shaft
    ================================================================================================================
    """
    print("Creating end components for MPC elements...")

    """
    For one year old and above the proximal component range is l/10 because the femoral head is more developed than 
    a younger infant. So to hold the proximal end correctly in the MPC constraint more area needs to be selected.
    For younger than one year old the range is l/20.
    """
    match var_ins.under_one_year:
        case True:
            prox_comp_range = var_ins.l / 20
        case False:
            prox_comp_range = var_ins.l / 10

    mapdl.nsel("S", "LOC", "X", x1_min+prox_comp_range, -1000)
    mapdl.nsel("R", "ext")
    mapdl.cm("proximal_end", "NODE")

    mapdl.allsel("all")

    mapdl.nsel("S", "LOC", "X", x1_max-prox_comp_range, -1000)
    mapdl.nsel("R", "ext")
    mapdl.cm("distal_end", "NODE")

    mapdl.allsel("all")

    # Find mid of proximal end

    mapdl.nsel("s", "loc", "x", x1_lower)  # Selects nodes within the lower segment
    mapdl.nsel("r", "ext")  # Selects external nodes
    mapdl.cm("proximal", "node")  # Creates a component called Proximal

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

    max_kp = mapdl.get_value("kp", "", "num", "max")  # Finds the maximum kp number

    # kp3 should be the same as the keypoint3 of sys11 as positive y should always point towards the prox ossification
    kp1 = max_kp + 1
    kp2 = max_kp + 2
    kp3 = max_kp + 3

    mapdl.k(kp1, xmid, ymid, zmid)  # Origin - mid-shaft
    mapdl.k(kp2, xdistal, ydistal, zdistal)  # Positive x
    mapdl.k(kp3, var_ins.proximal[0], var_ins.proximal[1], var_ins.proximal[2])  # Positive y

    mapdl.cskp(12, 0, kp1, kp2, kp3)  # Create local coordinate system 12

    mapdl.csys(12)
    mapdl.dsys(12)
    mapdl.nsel("all")
    mapdl.nrotat("all")

    """
    ================================================================================================================
    Create a pilot node at the proximal end for rotation reference
    ================================================================================================================
    """
    print("Creating pilot nodes for MPC elements...")

    max_node = int(mapdl.get_value("node", "", "num", "max"))  # Finds the maximum number of nodes
    pilot_node_1 = max_node + 1
    pilot_node_2 = max_node + 2

    x_pilot_1 = xprox - (var_ins.l/2)
    y_pilot_1 = yprox
    z_pilot_1 = zprox

    x_pilot_2 = xdistal + (var_ins.l/2)
    y_pilot_2 = ydistal
    z_pilot_2 = zdistal

    mapdl.n(pilot_node_1, x_pilot_1, y_pilot_1, z_pilot_1)  # Create first lead node
    mapdl.n(pilot_node_2, x_pilot_2, y_pilot_2, z_pilot_2)  # Create second lead node

    mapdl.allsel("all")
    mapdl.et(1, "mass21")  # Define mass element type for pilot nodes
    mapdl.r(1,1,1,1,.5,.5,.5,)
    mapdl.type(1)
    mapdl.real(1)
    mapdl.esys(0)
    mapdl.keyopt(2,1)
    mapdl.tshap("pilo")
    mapdl.e(pilot_node_1)
    mapdl.e(pilot_node_2)

    # follower nodes component is at the proximal end component since the pilot node is there

    """
    ================================================================================================================
    Define MPC element between the proximal pilot node and the follower nodes
    ================================================================================================================
    """
    print("Defining MPC elements between proximal pilot and follower nodes...")

    mapdl.cmsel("S", "proximal_end")  # Select proximal end nodes
    mapdl.nsel("A","","", pilot_node_1)
    nmast_ = pilot_node_1

    mapdl.nsel("U", "", "", nmast_)
    follower_nodes = mapdl.mesh.nnum  # Direct array of selected node numbers
    num_followers = len(follower_nodes)

    # Define MPC elements

    etmax = mapdl.get_value("etyp", 0, "num", "max")
    mapdl.et(etmax + 1, "mpc184")  # Define MPC element type for pilot nodes

    mapdl.keyopt(etmax + 1, 1, 1)
    mapdl.keyopt(etmax + 1, 2, 0)
    mapdl.type(etmax + 1)
    mapdl.real(etmax + 1)

    # Create MPC elements
    for i, follower in enumerate(follower_nodes, 1):
        mapdl.e(nmast_, int(follower))
        if i % 100 == 0:
            print(f"Created {i}/{num_followers} MPC elements")

    # mapdl.cmsel("S", "n_tmp")
    mapdl.nsel("A","","", nmast_)
    mapdl.esel("S", "TYPE", "", etmax + 1)
    mapdl.allsel("all")

    """
    ================================================================================================================
    Define MPC element between the distal pilot node and the follower nodes
    ================================================================================================================
    """
    print("Defining MPC elements between distal pilot and follower nodes...")

    mapdl.cmsel("S", "distal_end")  # Select distal end nodes
    mapdl.nsel("A","","", pilot_node_2)
    nmast_ = pilot_node_2

    mapdl.nsel("U", "", "", nmast_)
    follower_nodes = mapdl.mesh.nnum  # Direct array of selected node numbers
    num_followers = len(follower_nodes)

    # Define MPC elements

    etmax = mapdl.get_value("etyp", 0, "num", "max")
    mapdl.et(etmax + 1, "mpc184")  # Define MPC element type for pilot nodes

    mapdl.keyopt(etmax + 1, 1, 1)
    mapdl.keyopt(etmax + 1, 2, 0)
    mapdl.type(etmax + 1)
    mapdl.real(etmax + 1)

    # Create MPC elements
    for i, follower in enumerate(follower_nodes, 1):
        mapdl.e(nmast_, int(follower))
        if i % 100 == 0:
            print(f"Created {i}/{num_followers} MPC elements")

    # mapdl.cmsel("S", "n_tmp")
    mapdl.nsel("A", "", "", nmast_)
    mapdl.esel("S", "TYPE", "", etmax + 1)
    mapdl.allsel("all")

    """
    ================================================================================================================
    Applying boundary conditions for torsion
    Moment at the distal pilot node
    ================================================================================================================
    """
    print("Applying boundary conditions for torsion...")

    mapdl.csys(0)
    mapdl.dsys(0)

    mapdl.d(pilot_node_1, "uy", 0) # Fix y and z displacement of the proximal pilot node
    mapdl.d(pilot_node_1, "uz", 0)
    mapdl.d(pilot_node_1, "rotx", 0) # Fix rotation against the applied torque

    mapdl.d(pilot_node_2, "ux", 0) # Fix x displacement of the distal pilot node

    match var_ins.direc:
        case "internal":
            mapdl.f(pilot_node_2, "mx", var_ins.M)
        case "external":
            mapdl.f(pilot_node_2, "mx", -var_ins.M)

    return x1_max, x1_min

def solve_func(mapdl):
    """
    This function solves the model. Ready for export
    """
    mapdl.slashsolu()  # Enters solution mode
    print("Entered Solution Mode")
    # mapdl.nlgeom("on")  # Turns on non-linear geometry
    # print("Turned on NLGEOM")
    mapdl.eqslv("pcg", 1e-8)  # Sets the equation solver to PCG with a tolerance of 1e-8
    print("Turned on PCG")
    mapdl.solve()  # Solves the model
    print("Finished Solve")
    mapdl.save(str(var_ins.id) + "_" + "torsion", "db") # Saves the model
    print("Saved Solve")

def export_func(mapdl, xmax, xmin):
    """
    This function outputs the principle stress and strain results for the ROI.
    """
    mapdl.post1()  # Enters post-processing mode

    mapdl.inres("all")
    mapdl.file(str(var_ins.id) + "_" + "torsion", "rst")  # Loads the solved *.rst file
    mapdl.set("last") # Sets to the last load step

    mapdl.prep7()

    mapdl.allsel("all")
    mapdl.csys(12)
    mapdl.dsys(12)

    mapdl.nsle("S", "corner")

    """
    For one year old and above to ensure the ROI is only the shaft segment of the femur. The range for <=1 year is l/7.
    For younger than one year old the range is l/15.
    """
    match var_ins.under_one_year:
        case True:
            roi_result_range = var_ins.l / 15
        case False:
            roi_result_range = var_ins.l / 7

    mapdl.nsel("R", "LOC", "X", xmax - roi_result_range, xmin + roi_result_range)
    mapdl.nsel("R", "ext")

    var_ins.nodenum_roi = mapdl.get_value("node", "", "count") # Counts the number of nodes in the ROI

    # Define array to save xyz of selected nodes in ROI
    var_ins.roi_x = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for x coordinates of ROI nodes
    var_ins.roi_y = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for y coordinates of ROI nodes
    var_ins.roi_z = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for z coordinates of ROI nodes
    var_ins.roi_node = np.zeros(int(var_ins.nodenum_roi))  # Initialises empty array for node numbers of ROI nodes

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

    mapdl.allsel("all")

    mapdl.post1()

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
    var_ins.fname = int(var_ins.id)

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

def torsion():
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

    mapdl = launch_mapdl(nproc=gui_ins.core_count, additional_switches='-smp', loglevel="DEBUG", print_com=True,
                         cleanup_on_exit=True, set_no_abort=True)
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

    var_ins.py_rot = np.zeros(var_ins.step)
    var_ins.pz_rot = np.zeros(var_ins.step)
    var_ins.rad = np.zeros(var_ins.step)
    var_ins.angle = np.zeros(var_ins.step)
    var_ins.csys_num = np.zeros(var_ins.step)
    var_ins.kp_num = np.zeros(var_ins.step)

    try:
        xmax, xmin = local_func(mapdl)
        print("Local function complete")
    except Exception as e:
        print("can't do local function")
        for frame in traceback.extract_tb(sys.exc_info()[2]):
            fname, lineno, fn, text = frame
            print("Error in %s on line %d: %s" % (fname, lineno, text))
        print(f"Error: {e}")

    try:
        solve_func(mapdl)
        print("Solve function complete")
    except Exception as e:
        print("can't solve")
        print(f"Error: {e}")

    try:
        export_func(mapdl, xmax, xmin)
        print("Export function complete")
    except Exception as e:
        print("can't export")
        print(f"Error: {e}")

    mapdl.finish()
    mapdl.exit()
