# Welcome to PyPeCT2S Documentation

## Introduction

This work uses techniques and tools developed by the [INSIGNEO Institute](https://www.sheffield.ac.uk/insigneo) for the [CT2S](https://ct2s.insigneo.org/ct2s/) pipeline.

The goal of this work is to automate the [CT2S](https://ct2s.insigneo.org/ct2s/) pipeline steps, to use them in a modern setting in a repeatable and
user-friendly manner; with high adaptability and extensibility.

Use of this tool has resulted in pipeline time reductions of up to 70 %.

Scripts, methods, and work contained in this repository have been heavily based on works by 
[Dr Xinshan Li](https://scholar.google.co.uk/citations?user=T3t8XdcAAAAJ&hl=en) and 
[Dr Zainab Altai](https://scholar.google.com/citations?user=VaL--SsAAAAJ&hl=en).

Specific works of importance to this repository are: <ref>[1](#ref1), [2](#ref2), [3](#ref3), [4](#ref4)</ref>

## Contact

If you have any questions, please contact the authors:

George H. Allison ([Email](mailto:GHAllison1@sheffield.ac.uk) | [LinkedIn](https://www.linkedin.com/in/george-h-allison/)), 
Dr Xinshan Li ([Email](mailto:xinshan.li@sheffield.ac.uk))

If you have any additional queries regarding the CT2S pipeline, please contact the 
[INSIGNEO Institute](https://www.sheffield.ac.uk/insigneo).

## Disclaimer

This software has been designed for research purposes only and has not been reviewed or approved by medical device 
regulation bodies.

This software is not to be used alone or in combination, for human beings for one or more of the following specific 
medical purposes:

- diagnosis, prevention, monitoring, prediction, prognosis, treatment or alleviation of disease.
- diagnosis, monitoring, treatment, alleviation of, or compensation for, an injury or disability.
- investigation, replacement or modification of the anatomy or of a physiological or pathological process or
state.
- providing information by means of _in vitro_ examination of specimens derived from the human body, including
organ, blood and tissue donations.

Please note that this software is provided as is and without warranty. The authors are not responsible for any damage.

Please ensure you have the correct permissions to run the software and that you have the correct licenses for the software
you are using.

Please keep in mind the limits of the software this GUI interfaces with, and the limits of the software itself. _We
cannot solve issues that arise from software we do not control._ However, if you think there is an issue with the
GUI, please raise an issue on the repository.


## Feedback and Development

This software is in active development and will likely remain for the next few years. If you have any feedback, 
please raise an issue or open a discussion on the repository.

If you want to include your custom scripts, please raise an issue, open a discussion, or create a pull request 
on the repository. Alternatively, you can contact the authors directly.

Pull requests are welcome, but please ensure you have tested your changes before submitting.

## Project layout

    PyPeCT2S.py                     # The main run file.
    qt_gui.py                       # The main GUI file.
    requirements.txt                # The requirements file for reproducing the environment.
    README.md                       # The project README.
    LICENSE                         # The project license.

    core_libs/                      # The core libraries for the project.
        __init__.py                 # The core library init file.
        ansys_vars.py               # The ANSYS variables file.
        gui_funcs.py                # The GUI functions file.
        gui_vars.py                 # The GUI variables file.
        ldmk_funcs.py               # The landmark functions file.
        mat_vars.py                 # The material variables file.
        stl_checks.py               # The STL checks file.
        texteditredirector.py       # The text edit redirector file.
        waitingspinnerwidget.py     # The waiting spinner widget file.

    fem_libs/                       # The FEM libraries to load for the gui.
        __init__.py                 # init file to find all the FEM scripts on launch.
        A_APDL_4B_fem.py            # ANSYS APDL 4-Point Bending FEM script

    materials_libs/                 # The material libraries to load for the gui.
        __init__.py                 # init file to find all the material scripts on launch.
        Bonemat_cli.py              # Runs the Bonemat CLI from python.

    mesh_libs/                      # The meshing libraries to load for the gui.
        __init__.py                 # init file to find all the meshing scripts on launch.
        A_IA_mesher.py              # ANSYS ICEM CFD and APDL meshing script.

    post_libs/                      # The post-processing libraries to load for the gui.
        __init__.py                 # init file to find all the post-processing scripts on launch.
        A_post.py                   # ANSYS post-processing functionality.

    bonemat/
        ...                         # For placing personal Bonemat CLI executable.   

    docs/
        index.md                    # The documentation homepage.
        ...                         # Other markdown pages, images and other files.

## REFERENCES

<a id='ref1'>1</a>: Altai, Z., Viceconti, M., Offiah, A.C. et al. Investigating the mechanical response of paediatric 
bone under bending and torsion using finite element analysis. Biomechanics and Modeling in Mechanobiology 17, 1001–1009 
(2018). [DOI](https://doi.org/10.1007/s10237-018-1008-9)

<a id='ref2'>2</a>: Altai, Z., Muhammad, Q., Li, X. et al. The effect of boundary and loading conditions on patient 
classification using finite element predicted risk of fracture. Clinical Biomechanics 68, 137–143 
(2019). [DOI](https://doi.org/10.1016/j.clinbiomech.2019.06.004)

<a id='ref3'>3</a>: Li, X., Viceconti, M., Cohen, M.C. et al. Developing CT based computational models of pediatric 
femurs. Journal of Biomechanics 48, 2034–2040 
(2015). [DOI](https://doi.org/10.1016/j.jbiomech.2015.03.027)

<a id='ref4'>4</a>: Viceconti, M., Muhammad, Q., Bhattacharya, P. et al. Are CT-Based Finite Element Model Predictions 
of Femoral Bone Strengthening Clinically Useful? Current Osteoporosis Reports 16, 216–223 
(2018). [DOI](https://doi.org/10.1007/s11914-018-0438-8)