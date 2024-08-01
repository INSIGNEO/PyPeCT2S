# Troubleshooting

If you encounter any issues with the program, please try the following first:

- Ensure you have a licensed version of ANSYS available on your computer. You may require a VPN to be active.
- Ensure your version of ANSYS is 2021 or newer. ANSYS 2023R2 is the recommended version.
- Ensure you have launched both ANSYS ICEM and ANSYS APDL once before use.
- By default, all tabs except meshing are locked. If you require additional features contact the person who provided 
the program to you.

Issues are known to occur more frequently with managed IT systems, so please ensure you have the correct permissions to
run the software.

## Meshing

If you're having trouble with Meshing failing, try the following:

### ANSYS APDL Fails

One of the most common causes for ANSYS APDL to fail at the meshing step is actual due to an issue in the ICEM section.

Things to check for:

- STL integrity - Make sure your STL file is correct, not corrupted and has no visible issues.
- Mesh errors - Make sure you have gone over your mesh carefully and there are no errors like holes or broken surfaces.

### Unable to locate filename `XXXXXXXX.xxx`

This problem is often related to the case of the filename. The program is case-sensitive, however windows is not when
saving files. This means if there is alreadt a file with the same name but different case, the file will not save
correctly and the program will not be able to locate it; as it is looking for the exact case.

e.g. `filename.stl` and `FileName.stl` are two different files to the program. But windows will save them as the 
same file. Giving preference to the exist file saved.

## Material Application

If you're having trouble with your material application, try the following:

- Due to the automation steps to operate Bonemat seamlessly, model rotation is passed to an operation prior to meshing. 
If you need this, please either complete the Bonemat step manually or repeat meshing with the Bonemat rotation 
option selected. (See the [Checkboxes](usage.md#checkboxes) section for more information.)

## Finite Element Method

### Landmarks

If you're having trouble with landmarks, try the following:

- If you are not using paediatric femurs you must provide your own landmark files.
    - The current landmark system is designed for paediatric femurs only. 
- Ensure you have landmark files in the correct format, and they can be read by the program.

## ANSYS APDL

### General

If you're having trouble with ANSYS APDL, try the following:

- Ensure you have the correct version of ANSYS installed.
- Make sure you have launched ANSYS APDL at least once before using the program.
- Check for any syntax errors in your script.
- Ensure you have the correct permissions to run the software.
- Check which license you have and if its compatible with the core count you are trying to use.

## Custom Scripts

### General

If you're having trouble with custom scripts, try the following:

- Ensure your script has the required functions: `get_name()` and `gui_elements()`.
- Check for any syntax errors in your script.
- Make sure the script is saved in the correct folder and the program has been restarted.

### GUI Crashes, Freezes, or Errors when unfocused

If you're experiencing GUI crashes, freezes, or errors when the program is unfocused, try the following:

- Check you are using the correct parent_widget in your script. This can cause issues if not set correctly.
- Ensure you have the correct slots and signals set up in your script.
- Check for any infinite loops in your script.

## Issue not here?

If you have tried the above and are still experiencing issues, please raise an issue on the repository. Or contact the
person who provided the program to you or author directly. 

[Contact](index.md#contact).