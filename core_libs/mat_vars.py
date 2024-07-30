"""
================================================================================================================
Material Variables Class
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

class BMatVariables:
    def __init__(self, initial_vars=None):
        if initial_vars is None:
            self.cdb_path = ""  # Path to your cdb file
            self.vtk_path = ""  # Path to your vtk file
            self.config_path = ""  # Path to your config file
        else:
            # Initialize the instance variables with the values of initial_vars
            self.__dict__ = initial_vars.__dict__.copy()
