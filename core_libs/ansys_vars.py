"""
================================================================================================================
ANSYS VARIABLES
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


class MeshVariables:
    def __init__(self, initial_vars=None):
        if initial_vars is None:
            self.root_dir = '\\'
            self.max_element_size = 3.0  # Maximum element size
            self.proj_name = ""  # Project name
            self.icem_path = ""  # icemcfd.bat
            self.icem_ansys_path = ""  # This is found from icem_path
            self.file_name = ""  # File name is pulled by commands later, file name is pulled from stl_path
            self.file_name_ext = ""  # File name pulled by commands with extension later
            self.stl_type = ""  # Type of stl file
            self.icem_variables = [
                "icem_line_3_1", "icem_line_3_2", "icem_line_3_3", "icem_line_3_4", "icem_line_23_0",
                "icem_line_23_1", "icem_line_23_2", "icem_line_25_0", "icem_line_25_1", "icem_line_25_2",
                "icem_line_37_0", "icem_line_37_1", "icem_line_37_2", "icem_line_41_0", "icem_line_41_1",
                "icem_line_41_2", "icem_line_43_0", "icem_line_43_1", "icem_line_43_2", "icem_line_43_3",
                "icem_line_43_4", "icem_line_43_5", "icem_line_43_6", "icem_line_43_7", "icem_line_43_8",
                "icem_line_43_9", "icem_line_43_10", "icem_line_43_11", "icem_line_76_0", "icem_line_76_1",
                "icem_line_76_2", "icem_line_79_0", "icem_line_79_1", "icem_line_79_2", "icem_line_87_0",
                "icem_line_87_1", "icem_line_87_2", "icem_line_87_3", "icem_line_87_4", "icem_line_87_5",
                "icem_line_87_6", "icem_line_87_7", "icem_line_87_8", "icem_line_87_9", "icem_line_87_10",
                "icem_line_87_11", "icem_line_87_12", "icem_line_87_13", "icem_line_87_14", "icem_line_87_15",
                "icem_line_87_16", "icem_line_87_17", "icem_line_88_1", "icem_line_88_2", "icem_line_88_3",
                "icem_line_88_4"
            ]
            for icem_variable in self.icem_variables:
                setattr(self, icem_variable, "")
            self.icem_commands = []
            self.files_to_remove = ['temp_tetra.tin', 'tetra_cmd.log', 'tmpdomain0.uns', 'temp_icem_script.rpl']
        else:
            # Initialize the instance variables with the values of initial_vars
            self.__dict__ = initial_vars.__dict__.copy()


class FemVariables:
    def __init__(self, initial_vars=None):
        if initial_vars is None:
            self.id = ""  # Name of file
            self.manual = 2  # Specific orientation for bending [1 = solving one specific orientation but only for bending]
            self.mode = 1  # 1 - Four point bending | 2 - Torsion
            self.angle_inc = 10  # Increment for bone rotation about the x-axis [Set to 0 or 360 to calculate default orientation
            self.F = 120.00  # Compression force (N) [original script was at 120N]
            self.export_EX = 0  # 1 - Exporting EX values at mid-shaft
            self.pc = 0.5  # Percentage of remaining segment
            self.pf = 0.5  # Proportion of mid-segment where the force is applied
            self.direc = 2  # external rotation direction
            self.step = ""
            self.n = ""
            self.rad_inc = ""
            self.f_length = ""
            self.max_elem_size = ""
            self.py_rot = ""
            self.pz_rot = ""
            self.rad = ""
            self.angle = ""
            self.csys_num = ""
            self.kp_num = ""
            self.middle = np.zeros(3)  # Initialises empty array for middle landmark
            self.distal = np.zeros(3)  # Initialises empty array for distal landmark
            self.proximal = np.zeros(3)  # Initialises empty array for proximal landmark
            self.roi_x = ""
            self.roi_y = ""
            self.roi_z = ""
            self.roi_node = ""
            self.pstrain1 = ""
            self.pstrain3 = ""
            self.pstress1 = ""
            self.pstress3 = ""
            self.x_upper = ""
            self.x_lower = ""
            self.l_seg = ""
            self.fx_upper = ""
            self.fx_lower = ""
            self.l = ""
            self.nodenum_roi = ""
            self.fname = ""
            self.output_dir = ""
            self.working_dir = ""
        else:
            # Initialize the instance variables with the values of initial_vars
            self.__dict__ = initial_vars.__dict__.copy()


class PostVariables:
    def __init__(self, initial_vars=None):
        if initial_vars is None:
            self.id = ""  # Name of file
            self.F = 120.00  # Compression force (N) [original script was at 120N]
            self.pc = 0.5  # Percentage of remaining segment
            self.pf = 0.5  # Proportion of mid-segment where the force is applied
            self.x_upper = None
            self.x_lower = None
            self.fx_upper = None
            self.fx_lower = None
            self.l = ""
            self.working_dir = ""
            self.output_dir = ""
            self.force_to_failure = []
            self.moment_to_failure = []
            self.dt = np.dtype([('Angle', int), ('Max Tension', float), ('Tension Node', int),
                                ('Max Compression', float), ('Compression Node', int), ('Fail Type', 'U11'),
                                ('Force to Fail', float), ('Moment to Fail', float)])
            self.data = np.empty(0, dtype=self.dt)
        else:
            # Initialize the instance variables with the values of initial_vars
            self.__dict__ = initial_vars.__dict__.copy()

