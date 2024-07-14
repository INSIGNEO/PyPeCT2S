# PyPeCT2S - Pythonic Paediatric Computed Tomography to Strength [<img src='INSIGNEO.png' width='20'>](https://www.sheffield.ac.uk/insigneo)

## INTRODUCTION

This work uses techniques and tools developed by the [INSIGNEO Institute](https://www.sheffield.ac.uk/insigneo) for the [CT2S](https://ct2s.insigneo.org/ct2s/) pipeline.

The goal of this work is to automate the [CT2S](https://ct2s.insigneo.org/ct2s/) pipeline steps, to use them in a modern setting in a repeatable and user-friendly manner; with high adaptability.

Scripts and work contained in this repository have been heavily based on works by [Dr Xinshan Li](https://scholar.google.co.uk/citations?user=T3t8XdcAAAAJ&hl=en) and [Dr Zainab Altai](https://scholar.google.com/citations?user=VaL--SsAAAAJ&hl=en).

Specific works of importance to this repository are:

[Zainab Altai et al. | Investigating the mechanical response of paediatric bone under bending and torsion using finite element analysis](https://doi.org/10.1007/s10237-018-1008-9)

[Zainab Altai et al. | The effect of boundary and loading conditions on patient classification using finite element predicted risk of fracture](https://doi.org/10.1016/j.clinbiomech.2019.06.004)

[Xinshan Li et al. | Developing CT based computational models of pediatric femurs](https://doi.org/10.1016/j.jbiomech.2015.03.027)

[Marco Viceconti et al. | Are CT-Based Finite Element Model Predictions of Femoral Bone Strengthening Clinically Useful?](https://doi.org/10.1007/s11914-018-0438-8)

## USAGE

_Please only run the scripts if you are comfortable running Python scripts._

It is recommneded to use the latest release available under: [Releases](https://github.com/INSIGNEO/PyPeCT2S/releases/latest)

Fill in blank fields and press button to run. Information will display in the log window. Repeat for each tab required.

## REQUIREMENTS

>[!IMPORTANT]
> 
><span style="color:red">**An ANSYS install is required to run ANSYS based scripts**</span>
> 
> Make Sure you are connected to a licensing server before running.
>
>ANSYS scripts require a minimum ANSYS version to function correctly. 2023R2 and above is recommend, and the systems have been tested on 2021R2 up.

If you are looking to use automatic Bonemat-based material assignment, you will need to have the rolling version of [Bonemat]() available on your system and copy the `BonematCLI.exe` in to the Bonemat folder.

Please keep in mind the limits of the software this GUI interfaces with. _We cannot solve issues that arise for errors in software we do not control._

### Python Requirements

- [See requirements file](requirements.txt)

- Set up an environment as follows:
-   `pip install -r requirements.txt`

### File / Model / Input Requirements

You can start the process at any step by jumping to that tab.

If you wish to start fresh you require the following files:
- DICOM image scans contained in a `*.VTK` file.
- Segmented 3D `*.STL` model of the bone. (_**It is important you check the quality of segmentation, meshing will fail if there are external floating elements in the model.**_)
- Configuration file for material application, based on the specific CT scanner used.

## DISCLAIMER

This software has been designed for research purposes only and has not been reviewed or approved by medical device regulation bodies.

This software is not to be used alone or in combination, for human beings for one or more of the following specific medical purposes:
- diagnosis, prevention, monitoring, prediction, prognosis, treatment or alleviation of disease,
- diagnosis, monitoring, treatment, alleviation of, or compensation for, an injury or disability,
- investigation, replacement or modification of the anatomy or of a physiological or pathological process or
state,
- providing information by means of in vitro examination of specimens derived from the human body, including
organ, blood and tissue donations,
