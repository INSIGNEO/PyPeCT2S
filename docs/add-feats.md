# Additional Features

Below will be a list of additional features that are included in the software. But are not directly visible to users.

## Landmark Determination

These extra features are used to determine the landmarks of the bone. This is used to determine the orientation of the
bone and the location of the femoral head.

These are specific to paediatric femur models, if you do not have a paediatric femur model you should determine your 
landmarks yourself and make sure the files are accessible for the program.

If landmark files are present the program will not determine landmark points automatically.

Landmark files should be in the same working directory as the `*.cdb` file you are using in a folder called `landmarks`.

Landmark files should be in a plain text format with the following structure:

```
x, y, z
```

or 

```
x
y
z
```

There should be a file for each landmark point. The files should be named as follows:

- `RPOss.txt`: The proximal point of the bone.
- `RDOss.txt`: The distal point of the bone.
- `RMShaft.txt`: The center of mass of the bone.

### Calculation for the Length of the Bone

Purpose: Calculate the length of the bone by finding the maximum distance between vertices.

Mathematical Operation:

Let $( \mathbf{v}_i )$ be the vertices of the mesh.

Find the farthest vertex $\mathbf{v}_{\text{far}}$ from an arbitrary starting vertex $( \mathbf{v}_0 )$: 

$$
\mathbf{v}_{\text{far}} = \arg\max{\mathbf{v}_i} |\mathbf{v}_0 - \mathbf{v}_i|
$$

Find the maximum distance from $\mathbf{v}_{\text{far}}$: 

$$
\text{max distance} = \max{\mathbf{v}_i} |\mathbf{v}_{\text{far}} - \mathbf{v}_i|
$$

### Extension of Points Along the Central Long Axis

Purpose: Extend the distal and proximal points along the central axis by a given percentage of the bone length.

Mathematical Operation:

Calculate the central axis vector: 

$$
\mathbf{v}_{\text{axis}} = \mathbf{v}_{\text{distal}} - \mathbf{v}_{\text{proximal}}
$$

Calculate the bone length $L$: 

$$
L = \text{bone length}
$$

Calculate the extension length: 

$$
L_{\text{ext}} = L \times \left(\frac{\text{percentage}}{100}\right)
$$

Normalize the central axis vector: 

$$
\mathbf{d} = \frac{\mathbf{v}_{\text{axis}}}{L}
$$

Extend the distal and proximal points: 

$$
\mathbf{v}_{\text{distal}} = \mathbf{v}_{\text{distal}} + \mathbf{d} \times L_{\text{ext}}
$$ 

$$
\mathbf{v}_{\text{proximal}} = \mathbf{v}_{\text{proximal}} - \mathbf{d} \times L_{\text{ext}}
$$

### Estimate the Femoral Head Location

Purpose: Estimate the location of the femoral head based on the proximal, distal, and center of mass points.

Mathematical Operation:

Calculate the shaft axis: 

$$
\mathbf{v}_{\text{shaft}} = \mathbf{v}_{\text{proximal}} - \mathbf{v}_{\text{distal}}
$$

Calculate the vector to the center of mass: 

$$
\mathbf{v}_{\text{com}} = \mathbf{v}_{\text{com}} - \mathbf{v}_{\text{proximal}}
$$

Estimate the distance to the femoral head: 

$$
d_{\text{head}} = |\mathbf{v}_{\text{shaft}}| \times \left(\frac{\text{percentage}}{100}\right)
$$

Calculate a perpendicular vector: 

$$
\mathbf{v}_{\perp} = \mathbf{v}_{\text{shaft}} \times \mathbf{v}_{\text{com}}
$$

Calculate the direction to the femoral head: 

$$
\mathbf{v}_{\text{head_dir}} = \mathbf{v}_{\perp} \times \mathbf{v}_{\text{shaft}}
$$

$$
\mathbf{v}_{\text{head_dir_norm}} = \frac{\mathbf{v}_{\text{head_dir}}}{|\mathbf{v}_{\text{head_dir}}|}
$$

Estimate the femoral head location: 

$$
\mathbf{v}_{\text{head}} = \mathbf{v}_{\text{proximal}} - \mathbf{v}_{\text{head_dir_norm}} \times d{_\text{head}}
$$

### Find the Long Shaft Axis of the Bone

Purpose: Find the long shaft axis of the bone and estimate the femoral head location.

Mathematical Operation:
Calculate the center of mass: 

$$
\mathbf{v}_{\text{com}} = \frac{1}{N} \sum{i=1}^{N} \mathbf{v}_i
$$

Calculate the covariance matrix: 

$$
\mathbf{C} = \frac{1}{N-1} \sum_{i=1}^{N} (\mathbf{v}_i - \mathbf{v}_{\text{com}})(\mathbf{v}_i - \mathbf{v}_{\text{com}})^T
$$

Calculate the principal axes (eigenvectors): 

$$
\mathbf{C} \mathbf{e}_i = \lambda_i \mathbf{e}_i
$$

The shaft axis is the eigenvector with the largest eigenvalue: 

$$
\mathbf{v}_{\text{shaft}} = \mathbf{e}{max}(\lambda)
$$

Project vertices onto the shaft axis: 

$$
\mathbf{p}_i = (\mathbf{v}_i - \mathbf{v}_{\text{com}}) \cdot \mathbf{v}_{\text{shaft}}
$$

Find the proximal and distal points: 

$$
\mathbf{v}_{\text{proximal}} = \mathbf{v}_{min}(\mathbf{p}_i)
$$

$$
\mathbf{v}_{\text{distal}} = \mathbf{v}_{max}(\mathbf{p}_i)
$$

Estimate the femoral head location and extend points along the central axis as described above.


## STL Checks

To try and ensure the quality of the STL file, the software will run a series of checks on the file before running the
meshing script. These checks are not exhaustive, and you should check the file yourself. The checks are as follows:

### Check Non-manifold edges

_Purpose:_ Checks for edges shared by more than two faces, indicating non-manifold edges.  

_Description:_ This function iterates through all the faces of the STL mesh and counts the occurrences of each edge. 
Edges shared by more than two faces are considered non-manifold.  

### Check Multiple Bodies

_Purpose:_ Checks for multiple bodies in the STL file by identifying unconnected components.  

_Description:_ This function uses a depth-first search (DFS) algorithm to identify unconnected components in the mesh. 
Each unconnected component is considered a separate body.  

### check_non_uniform_scaling

_Purpose:_ Checks for non-uniform scaling in the STL mesh.

_Description:_ This function calculates the bounding box of the mesh and checks if the dimensions 
are uniformly scaled. Non-uniform scaling is detected if the dimensions are not proportional.  

### Check for Faces with Zero Area

_Purpose:_ Checks for degenerate faces (faces with zero area).  

_Description:_ This function iterates through all the faces of the STL mesh and calculates the area of each face. 
Faces with zero area are considered degenerate.  

### Check for Inverted Normals

_Purpose:_ Checks if normals are consistently oriented.  

_Description:_ This function calculates the center of the mesh and checks if the normals of the faces 
generally point outward. A simple heuristic is used to determine the orientation of the normals.  

### Check for Holes in the Mesh

_Purpose:_ Checks for holes by ensuring each edge is shared by exactly two faces.  

_Description:_ This function iterates through all the faces of the STL mesh and counts the occurrences of each edge. 
Edges shared by only one face are considered holes.  

### Check for Duplicate Vertices and Faces

_Purpose:_ Checks for duplicate vertices and faces.

_Description:_ This function identifies and counts duplicate vertices and faces in the STL mesh.