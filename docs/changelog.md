# Changelog:

## 1.0.2

- Fixed issue in meshing script where it would look for a temporary file that it did not need to unless certain
conditions were met.

## 1.0.1

- Made the inputs freeze while a function is running. 
This prevents variables changing and starting a function multiple times.
- Changed tempfile functionality to delete file after use.
- Changed from local offline documentation in the program to online documentation.
- Cleaned some documentation up.
- Minor fixes.

## 1.0.0

- Initial release of the software.
- Includes the following features:
  - Meshing with ANSYS ICEM CFD and APDL.
  - Material application with Bonemat CLI.
  - FEM script for 4-point bending in ANSYS APDL.
  - Post-processing in ANSYS.