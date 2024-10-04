"""
================================================================================================================
Landmark Functions
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
from stl import mesh
import os
from core_libs import gui_funcs, gui_vars

gui_ins = gui_vars.GuiVariables()


def reshape_1d_array(array):
    if array.ndim == 1 and array.shape[0] != 3:
        # If it's a 1D array with more than 3 elements, reshape to 2D and select the first row
        array = array.reshape((-1, 3))[0]
    elif array.ndim > 1:
        # If it's already a 2D array, select the first row
        array = array[0]

    return array


def bone_length(mesh_data):
    vertices = mesh_data.vectors.reshape(-1, 3)

    # Pick an arbitrary vertex as the starting point
    start_vertex = vertices[0]

    # Find the vertex farthest from the starting point
    max_distance = 0
    farthest_vertex = start_vertex
    for vertex in vertices:
        distance = np.linalg.norm(start_vertex - vertex)
        if distance > max_distance:
            max_distance = distance
            farthest_vertex = vertex

    # Find the vertex farthest from the farthest_vertex
    max_distance = 0
    for vertex in vertices:
        distance = np.linalg.norm(farthest_vertex - vertex)
        if distance > max_distance:
            max_distance = distance

    return max_distance


def extend_points_along_central_axis(distal, proximal, percentage, mesh_data):

    # Calculate the vector from proximal to distal point
    central_axis_vector = np.array(distal) - np.array(proximal)

    # Calculate the length of the bone
    try:
        bone_l = bone_length(mesh_data)
    except Exception as e:
        print(f"Error calculating bone length: {e}")

    # Calculate the extension length
    extension_length = bone_l * (percentage / 100.0)

    # Normalize the central axis vector to get the direction
    direction = central_axis_vector / bone_l

    # Extend the distal and proximal points
    distal = np.array(distal) + direction * extension_length
    proximal = np.array(proximal) - direction * extension_length

    # Convert back to tuples for consistency
    distal_point = tuple(distal)
    proximal_point = tuple(proximal)

    return distal_point, proximal_point


def estimate_femoral_head_location(proximal, distal, center_of_mass, mesh_data, percentage):

    # proximal = reshape_1d_array(proximal)
    # distal = reshape_1d_array(distal)
    center_of_mass = reshape_1d_array(center_of_mass)

    shaft_axis = np.array(proximal) - np.array(distal)

    # Vector from proximal to center of mass
    to_center_vector = np.array(center_of_mass) - np.array(proximal)

    # Estimate distance from proximal point to femoral head center
    # This distance can be adjusted based on anatomical data or preferences
    estimated_distance = np.linalg.norm(shaft_axis) * (percentage / 100.0)

    # Calculate a vector perpendicular to the shaft axis in the plane defined by proximal, distal, and center of mass
    perpendicular_vector = gui_funcs.crossing(shaft_axis, to_center_vector)
    direction_to_femoral_head = gui_funcs.crossing(perpendicular_vector, shaft_axis)
    # perpendicular_vector = np.cross(shaft_axis, to_center_vector)
    # direction_to_femoral_head = np.cross(perpendicular_vector, shaft_axis)
    direction_to_femoral_head_normalized = direction_to_femoral_head / np.linalg.norm(direction_to_femoral_head)

    # Calculate estimated femoral head location
    femoral_head_location = np.array(proximal) - direction_to_femoral_head_normalized * estimated_distance

    # Ensure the movement is in the correct direction
    if np.dot(femoral_head_location - np.array(proximal), shaft_axis) < 0:
        femoral_head_location = np.array(proximal) + direction_to_femoral_head_normalized * estimated_distance

    # Additional check to ensure the femoral head is in the anatomically correct direction
    if femoral_head_location[2] < proximal[2]:
        femoral_head_location = np.array(proximal) + direction_to_femoral_head_normalized * estimated_distance

    return femoral_head_location

def correct_distal_landmark(distal, mesh_data, slice_offset=5):
    vertices = mesh_data.vectors.reshape(-1, 3)

    # Find the distal end by identifying the minimum z-coordinate
    distal_z = np.min(vertices[:, 2])

    # Adjust the distal_z to be a few slices above the minimum
    unique_z_values = np.unique(vertices[:, 2])
    if len(unique_z_values) > slice_offset:
        distal_z = unique_z_values[slice_offset]

    # Filter vertices that are close to the distal end
    tolerance = 1e-3  # Adjust tolerance as needed
    distal_vertices = vertices[np.abs(vertices[:, 2] - distal_z) < tolerance]

    # Calculate the centroid of the distal vertices
    centroid = np.mean(distal_vertices, axis=0)

    # Calculate the covariance matrix and its eigenvalues and eigenvectors
    cov_matrix = np.cov(distal_vertices - centroid, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eig(cov_matrix)

    # Align the distal vertices with the principal axes
    rotation_matrix = eigenvectors.T
    aligned_vertices = (distal_vertices - centroid) @ rotation_matrix.T

    # Calculate the bounding box of the aligned distal vertices
    min_coords = np.min(aligned_vertices, axis=0)
    max_coords = np.max(aligned_vertices, axis=0)

    # Calculate the midpoints of the bounding box edges at the distal end
    midpoint_left_right = (min_coords[0] + max_coords[0]) / 2
    midpoint_front_back = (min_coords[1] + max_coords[1]) / 2
    distal_z = min_coords[2]  # Assuming the distal end is at the minimum z-coordinate

    # Calculate the intersection point in the aligned coordinate system
    intersection_point_aligned = np.array([midpoint_left_right, midpoint_front_back, distal_z])

    # Transform the intersection point back to the original coordinate system
    intersection_point = intersection_point_aligned @ rotation_matrix + centroid

    # Correct the distal landmark
    corrected_distal = (intersection_point + distal) / 2

    return corrected_distal


def find_long_shaft_axis(vari, mesh_data):
    # Calculate the middle of the long shaft
    vertices = mesh_data.points
    center_of_mass = np.mean(vertices, axis=0)

    # Calculate the covariance matrix of the model
    covariance_matrix = np.cov(vertices, rowvar=False)

    # Calculate the principal axes of the model
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

    # The longest principal axis is the shaft axis
    shaft_axis = eigenvectors[:, np.argmax(eigenvalues)]

    # The proximal and distal coordinates are the points on the model that are furthest along the shaft axis
    projections = np.dot(vertices - center_of_mass, shaft_axis)
    proximal_point = vertices[np.argmin(projections)]
    distal_point = vertices[np.argmax(projections)]
    middle_point = center_of_mass

    proximal_point = reshape_1d_array(proximal_point)
    distal_point = reshape_1d_array(distal_point)

    if proximal_point[2] < distal_point[2]:
        proximal_point, distal_point = distal_point, proximal_point

    # Correct the distal landmark
    try:
        distal_point = correct_distal_landmark(distal_point, mesh_data, 5)
    except Exception as e:
        print(f"Error correcting distal landmark: {e}")

    # Extend the distal and proximal points along the central axis
    try:
        distal_point, proximal_point = extend_points_along_central_axis(distal_point, proximal_point, 2, mesh_data)
    except Exception as e:
        print(f"Error estimating extended locations: {e}")

    # Estimate the location of the femoral head
    try:
        proximal_point = estimate_femoral_head_location(proximal_point, distal_point, middle_point, mesh_data,5)
        # print("Nothing for now")
    except Exception as e:
        print(f"Error estimating femoral head location: {e}")

    # Get the x, y, and z coordinates of the distal, proximal, and middle points
    match gui_ins.bm_rot:
        case True:
            vari.distal = - distal_point[0], - distal_point[1], distal_point[2]
            vari.proximal = - proximal_point[0], - proximal_point[1], proximal_point[2]
            vari.middle = - middle_point[0], - middle_point[1], middle_point[2]
        case False:
            vari.distal = distal_point[0], distal_point[1], distal_point[2]
            vari.proximal = proximal_point[0], proximal_point[1], proximal_point[2]
            vari.middle = middle_point[0], middle_point[1], middle_point[2]

    return mesh_data


def read_landmark_file(file_path, vari):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        if ',' in lines[0]:
            # Format: x, y, z
            landmarks = np.array([list(map(float, line.strip().split(','))) for line in lines])
        else:
            # Format: x \n y \n z
            landmarks = np.array([list(map(float, lines[i:i + 3])) for i in range(0, len(lines), 3)])

    landmarks = reshape_1d_array(landmarks)
    landmarks = tuple(landmarks)

    # Assign landmarks to vari attributes based on file name
    file_name = os.path.basename(file_path)
    if file_name == 'RMShaft.txt':
        vari.middle = landmarks
        np.savetxt(f"{vari.output_dir}/RMShaft.txt", vari.middle, delimiter=",", fmt='%.10f')
    elif file_name == 'RDOss.txt':
        vari.distal = landmarks
        np.savetxt(f"{vari.output_dir}/RDOss.txt", vari.distal, delimiter=",", fmt='%.10f')
    elif file_name == 'RPOss.txt':
        vari.proximal = landmarks
        np.savetxt(f"{vari.output_dir}/RPOss.txt", vari.proximal, delimiter=",", fmt='%.10f')
    else:
        raise ValueError(f"Unexpected file name: {file_name}")


def find_landmarks(vari):
    # Load STL file
    femur_mesh = gui_funcs.load_stl(gui_ins.stl_path)

    # Find the middle of the long shaft and align it with the x-axis
    femur_mesh = find_long_shaft_axis(vari, femur_mesh)

    print("Middle point:", vari.middle)
    print("Distal point:", vari.distal)
    print("Proximal point:", vari.proximal)
    np.savetxt(f"{vari.output_dir}/RMShaft.txt", vari.middle, delimiter=",", fmt='%.10f')
    np.savetxt(f"{vari.output_dir}/RDOss.txt", vari.distal, delimiter=",", fmt='%.10f')
    np.savetxt(f"{vari.output_dir}/RPOss.txt", vari.proximal, delimiter=",", fmt='%.10f')
