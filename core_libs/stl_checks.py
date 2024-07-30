"""
================================================================================================================
STL Check Module for checking the integrity of STL files prior to meshing.
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
from collections import defaultdict
from core_libs import gui_funcs


class STLChecks:
    def __init__(self, stl_path):
        self.stl_path = stl_path
        self.stl_mesh = gui_funcs.load_stl(self.stl_path)
        self.checks()

    def check_non_manifold_edges(self):
        # This function checks for edges shared by more than two faces, indicating non-manifold edges.
        edges = {}  # Dictionary to store edges and their counts
        for face in self.stl_mesh.vectors:
            for i in range(3):
                edge = tuple(sorted([tuple(face[i]), tuple(
                    face[(i + 1) % 3])]))  # Sort the vertices to get a consistent edge representation
                if edge in edges:
                    edges[edge] += 1  # Increment the count if the edge is already in the dictionary
                else:
                    edges[edge] = 1  # Add the edge to the dictionary if it's not already present
        non_manifold_edges = {edge: count for edge, count in edges.items() if
                              count > 2}  # Filter edges with more than two faces
        return non_manifold_edges

    def check_multiple_bodies(self):
        """
        Check for multiple bodies in the STL file by identifying unconnected components.
        """
        vertices = self.stl_mesh.vectors.reshape(-1, 3)
        vertex_indices = {tuple(vertex): idx for idx, vertex in enumerate(vertices)}
        adjacency_list = defaultdict(list)

        # Build the adjacency list
        for face in self.stl_mesh.vectors:
            for i in range(3):
                v1 = tuple(face[i])
                v2 = tuple(face[(i + 1) % 3])
                adjacency_list[vertex_indices[v1]].append(vertex_indices[v2])
                adjacency_list[vertex_indices[v2]].append(vertex_indices[v1])

        visited = set()

        def dfs(v):
            stack = [v]
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    stack.extend(adjacency_list[current])

        bodies = 0
        for vertex in vertex_indices.values():
            if vertex not in visited:
                dfs(vertex)
                bodies += 1

        return bodies

    def check_non_uniform_scaling(self):
        """
        Check for non-uniform scaling in the STL mesh.
        """
        vertices = self.stl_mesh.vectors.reshape(-1, 3)

        # Calculate the bounding box
        min_coords = vertices.min(axis=0)
        max_coords = vertices.max(axis=0)
        dimensions = max_coords - min_coords

        # Check for non-uniform scaling
        return not np.allclose(dimensions / dimensions[0], 1)

    def check_degenerate_faces(self):
        """
        Check for degenerate faces (faces with zero area).
        """
        degenerate_faces = []
        for i, face in enumerate(self.stl_mesh.vectors):
            if np.linalg.norm(gui_funcs.crossing(face[1] - face[0], face[2] - face[0])) == 0:
                degenerate_faces.append(i)
        return degenerate_faces

    def check_normals_orientation(self):
        """
        This function checks if normals are consistently oriented.
        A simple heuristic is used here: normals should generally point outward.
        """
        center = self.stl_mesh.points.mean(axis=0)[0:3]  # Calculate the center of the mesh
        outward_normals = True
        for normal, vector in zip(self.stl_mesh.normals, self.stl_mesh.vectors):
            face_center = vector.mean(axis=0)  # Calculate the center of the face
            direction_to_center = center - face_center  # Calculate the direction to the center of the mesh
            if np.dot(normal, direction_to_center) > 0:  # Check if the normal points outward
                outward_normals = False
                break
        return outward_normals

    def check_for_holes(self):
        # This function checks for holes by ensuring each edge is shared by exactly two faces.
        edges = {}
        for face in self.stl_mesh.vectors:
            for i in range(3):
                edge = tuple(sorted([tuple(face[i]), tuple(
                    face[(i + 1) % 3])]))  # Sort the vertices to get a consistent edge representation
                edges[edge] = edges.get(edge, 0) + 1  # Increment the count for the edge
        holes = [edge for edge, count in edges.items() if count == 1]  # Filter edges shared by only one face
        return holes

    def check_duplicate_vertices_faces(self):
        # This function checks for duplicate vertices and faces.
        unique_vertices = np.unique(self.stl_mesh.vectors.reshape(-1, self.stl_mesh.vectors.shape[-1]),
                                    axis=0)  # Reshape the vertices and find unique rows
        duplicate_vertices = self.stl_mesh.vectors.shape[0] * 3 - unique_vertices.shape[
            0]  # Calculate the number of duplicate vertices
        unique_faces = np.unique(self.stl_mesh.vectors, axis=0)  # Find unique faces
        duplicate_faces = self.stl_mesh.vectors.shape[0] - unique_faces.shape[0]  # Calculate the number of duplicate faces
        return duplicate_vertices, duplicate_faces

    def checks(self):
        # Load the STL file
        self.stl_mesh = gui_funcs.load_stl(self.stl_path)

        non_manifold_edges = self.check_non_manifold_edges()
        normals_orientation = self.check_normals_orientation()
        holes = self.check_for_holes()
        duplicate_vertices, duplicate_faces = self.check_duplicate_vertices_faces()
        multiple_bodies = self.check_multiple_bodies()
        degenerate_faces = self.check_degenerate_faces()
        non_uniform_scaling = self.check_non_uniform_scaling()

        if any([non_manifold_edges, holes, multiple_bodies > 1, degenerate_faces]):
            print("\n-------------------ERROR-------------------")
            if non_manifold_edges:
                print(f"Non-manifold edges: {len(non_manifold_edges)}")
            if holes:
                print(f"Holes in the model: {len(holes)}")
            if multiple_bodies:
                print(f"Multiple bodies: {multiple_bodies}")
            if degenerate_faces:
                print(f"Degenerate faces: {degenerate_faces}")
            print(
                "These will likely cause issues with the meshing process, please fix the issues above before proceeding.\n"
                "It is recommended to check your STL file for errors using a 3D viewer such as Slicer or ParaView.\n"
                "---------------------------------------------\n"
            )

        if any([normals_orientation == False, duplicate_faces, duplicate_vertices, non_uniform_scaling]):
            print("\n-------------------WARNING-------------------")
            if not normals_orientation:
                print("Normals are not correctly oriented.")
            if non_uniform_scaling:
                print(f"Non-uniform scaling: {non_uniform_scaling}")
            if duplicate_vertices:
                print(f"Duplicate vertices: {duplicate_vertices}")
            if duplicate_faces:
                print(f"Duplicate faces: {duplicate_faces}")
            print(
                "These issues may affect the meshing process.\n"
                "It is recommended to check your STL file for errors using a 3D viewer such as Slicer or ParaView.\n"
                "---------------------------------------------\n"
            )
