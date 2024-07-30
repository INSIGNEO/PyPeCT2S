"""
================================================================================================================
GUI Variables
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
import psutil
from PyQt6.QtCore import QThreadPool


class GuiBase:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(GuiBase, cls).__new__(cls, *args, **kwargs)
        return cls._instances[cls]


class GuiVariables(GuiBase):
    def __init__(self, initial_vars=None):
        if initial_vars is None:
            self.stl_path = ""  # Path to your stl file
            self.save_path = ""  # Path you want to save to
            self.output_dir = ""  # Path to your output directory, set later on when required
            self.file_name = ""  # File name is pulled by commands later, file name is pulled from stl_path
            self.file_name_ext = ""  # File name pulled by commands with extension later
            self.core_count = 1
            self.phys_core = psutil.cpu_count(logical=False)
            self.batch_mode = False  # True - Batch Mode | False - Single Model Mode. Not implemented yet.
            self.threadpool = QThreadPool()
            self.app_path = ""
            self.bm_rot = False  # True - Model was rotated in bonemat | False - Model was not rotated in bonemat

        else:
            # Initialize the instance variables with the values of initial_vars
            self.__dict__ = initial_vars.__dict__.copy()
