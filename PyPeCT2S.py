"""
================================================================================================================
PyPeCT2S: Pythonic Paediatric Computed Tomography to Strength
================================================================================================================
    Created by G.H. Allison, University of Sheffield, Sheffield, United Kingdom.
    Copyright (C) 2024 George H. Allison
    Contact: ghallison1@sheffield.ac.uk or xinshan.li@sheffield.ac.uk
----------------------------------------------------------------------------------------------------------------

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

________________________________________________________________________________________________________________
"""

from qt_gui import MyApplication
import sys
import traceback
import faulthandler
import time
import os
import glob
import subprocess
import psutil
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import math
import queue
from concurrent.futures import ThreadPoolExecutor
from stl import mesh
from ansys.mapdl.core import launch_mapdl
from ansys.dpf import post
from PyQt6.QtWidgets import QApplication, QTabWidget, QGridLayout, QStyleFactory, QWidget, QVBoxLayout, QMessageBox, QSizePolicy, QTextEdit, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSpinBox, QDoubleSpinBox, QCheckBox
from PyQt6.QtGui import QPalette, QColor, QTextCursor, QIcon, QPixmap, QGuiApplication, QPainter
from PyQt6.QtCore import QCoreApplication, pyqtSlot, QRunnable, QThreadPool, QMutex, QThread, Qt, QTimer
from PyQt6.QtSvg import QSvgGenerator


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyApplication()
    app.main_window = ex
    ex.init_ui()
    ex.show()
    sys.exit(app.exec())
