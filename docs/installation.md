# Installation and Requirements

## External Software Requirements

> 
><span style="color:red">**An ANSYS install is required to run ANSYS based scripts**</span>
> 
> Make Sure you are connected to a licensing server before running.
>
>ANSYS scripts require a minimum ANSYS version (2021R2) to function correctly. 2023R2 and above is recommended, and the 
> systems have been tested on 2021R2 up.
> 
> ANSYS software will need to be launched at least once before it can be used with the GUI.

>To use Bonemat features you must provide your own Bonemat CLI executable. 
>This can be placed in the `bonemat/` directory.
> 
>You will need to have the **_rolling_** version
>of [Bonemat](https://ior-bic.github.io/software/bonemat/) available on your system and copy the `BonematCLI.exe`, this
> can be found in `C:\Program Files\BIC Software\Bonemat\bin\BonematCLI.exe`.
>
>We will not distribute a copy of Bonemat with is software.

## From Release

### Windows

- Download the latest release from the [releases page](https://github.com/INSIGNEO/PyPeCT2S/releases).
- Extract the contents of the zip file to a directory of your choice.
- Run the `PyPeCT2S.exe` file to start the software.
- If you are using ANSYS, make sure you have the software installed and licensed.
- If you are using Bonemat, make sure you have the software installed and have copied the CLI.

- If you have additional scripts, you can place them in the appropriate directories in the appropriate directory 
(e.g. `fem_libs/`, `mesh_libs/`). You will need to restart the software to see the changes.

## From Source

1. Clone the Repository:  
    - Open a terminal or command prompt.
    - Navigate to the directory where you want to clone the repository.
    - Run the following command to clone the repository: 

    ```shell
    git clone https://github.com/INSIGNEO/PyPeCT2S.git
    ```

2. Change into the project directory:
   
    ```shell
    cd PyPeCT2S
    ```

3. Set Up a Virtual Environment:  
   It is recommended to use a virtual environment to manage dependencies.
       - Create a virtual environment:
       
    ```shell
    python -m venv venv
    ```

      - Activate the virtual environment:

    === "Windows"
    
        ```wsh
        venv\Scripts\activate
        ```

    === "macOS/Linux"

        ```shell
        source venv/bin/activate
        ```

      - Ensure you have pip installed and updated: 
 
      ```shell
      python -m pip install --upgrade pip
      ```
    
      - Upgrade setuptools:
      
      ```shell
      pip install --upgrade setuptools
      ```
   
      - Install the required packages from the requirements.txt file: 
   
      ```shell
      pip install -r requirements.txt
      ```

      - Verify the Installation by checking that all required packages are installed correctly: 
   
      ```shell
      pip list
      ```
   
4. Install the latest Microsoft Visual C++ Redistributable if you are using Windows:  
    - Download and install the latest version of the Microsoft Visual C++ Redistributable from the [Microsoft website](https://support.microsoft.com/en-us/help/2977003/the-latest-supported-visual-c-downloads).

5. Additional Setup for External Software:  
       - ANSYS:
         - Ensure ANSYS is installed and licensed.
         - Make sure you are connected to a licensing server before running ANSYS scripts.
         - ANSYS scripts require a minimum version of 2021R2. Version 2023R2 or above is recommended.
       - Bonemat:
         - Download and install the Bonemat CLI executable.
         - Create a directory named `bonemat/` in the project directory.
         - Place the BonematCLI.exe in the `bonemat/` directory.
         - Ensure you have the rolling version of Bonemat available on your system.

6. Run the Software:
    - Run the software by executing the following command in the terminal:

    ```shell
    python PyPeCT2S.py
    ```


    
