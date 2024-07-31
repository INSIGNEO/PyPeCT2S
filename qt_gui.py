"""
================================================================================================================
Qt GUI for PyPeCT2S
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

import sys
import os
import numpy as np
import importlib.util
import glob
from PyQt6.QtWidgets import QTabWidget, QComboBox, QStyleFactory, QWidget, QVBoxLayout, QMessageBox, QSizePolicy, \
    QTextEdit, QHBoxLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QCheckBox, QToolTip
from PyQt6.QtGui import QColor, QIcon, QGuiApplication
from PyQt6.QtCore import QCoreApplication, Qt
import core_libs
from core_libs import *
import fem_libs
from fem_libs import *
import mesh_libs
from mesh_libs import *
import post_libs
from post_libs import *


class MyApplication(QWidget):
    def __init__(self, *args, **kwargs):
        super(MyApplication, self).__init__(*args, **kwargs)

        if sys.stdout is None:
            sys.stdout = open(os.devnull, "w")
        if sys.stderr is None:
            sys.stderr = open(os.devnull, "w")

        """
        ----------------------------
        Variables
        ----------------------------
        """

        self.gui_vars = core_libs.gui_vars.GuiVariables()

        # If running as a frozen executable, use sys._MEIPASS
        if getattr(sys, 'frozen', False):
            self.application_path = sys._MEIPASS
        else:
            self.application_path = os.path.dirname(os.path.realpath(__file__))

        np.set_printoptions(precision=4, floatmode='fixed')

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.tab = QTabWidget(self)

        self.setWindowIcon(QIcon(os.path.join(self.application_path, 'icons/INSIGNEO.png')))

        # Script Dropdowns
        drop_layout = QHBoxLayout()
        drop_widget = QWidget()

        # Meshing Dropdown
        self.msh_dropdown = QComboBox()
        self.msh_dropdown.currentIndexChanged.connect(lambda: self.load_script_content(self.msh_dropdown, "Meshing"))
        self.discover_scripts(self.msh_dropdown, "mesh")

        # Material Dropdown
        self.mat_dropdown = QComboBox()
        self.mat_dropdown.currentIndexChanged.connect(lambda: self.load_script_content(self.mat_dropdown, "Material"))
        self.discover_scripts(self.mat_dropdown, "material")

        # FEM Dropdown
        self.fem_dropdown = QComboBox()
        self.fem_dropdown.currentIndexChanged.connect(lambda: self.load_script_content(self.fem_dropdown, "FEM"))
        self.discover_scripts(self.fem_dropdown, "fem")

        # Results Dropdown
        self.res_dropdown = QComboBox()
        self.res_dropdown.currentIndexChanged.connect(lambda: self.load_script_content(self.res_dropdown, "Results"))
        self.discover_scripts(self.res_dropdown, "post")

        drop_layout.addWidget(self.msh_dropdown)
        drop_layout.addWidget(self.mat_dropdown)
        drop_layout.addWidget(self.fem_dropdown)
        drop_layout.addWidget(self.res_dropdown)
        drop_widget.setLayout(drop_layout)

        # STL Path
        stl_layout = QHBoxLayout()
        stl_label = QLabel("STL Path:")
        self.stl_path_edit = QLineEdit()
        self.stl_path_edit.setPlaceholderText("Max 248 characters")
        self.stl_path_edit.setObjectName('stl_path_box')
        stl_browse_btn = QPushButton("Browse")
        stl_browse_btn.clicked.connect(lambda: core_libs.gui_funcs.browse_file_path('Select STL File', self.gui_vars, 'stl_path', 'STL Files (*.stl);;All Files (*)', 'stl_path_box', self))
        stl_layout.addWidget(stl_label)
        stl_layout.addWidget(self.stl_path_edit)
        stl_layout.addWidget(stl_browse_btn)

        # Save Path
        save_layout = QHBoxLayout()
        save_label = QLabel("Save Path:")
        self.save_path_edit = QLineEdit()
        self.save_path_edit.setPlaceholderText("Max 248 characters")
        self.save_path_edit.setObjectName('save_path_box')
        save_browse_btn = QPushButton("Browse")
        save_browse_btn.clicked.connect(lambda: core_libs.gui_funcs.browse_dir_path('Select Save Path', self.gui_vars, 'save_path', 'save_path_box', self))
        save_layout.addWidget(save_label)
        save_layout.addWidget(self.save_path_edit)
        save_layout.addWidget(save_browse_btn)

        # Core Count
        core_layout = QHBoxLayout()
        core_count_label = QLabel("Core Count:")
        self.core_count_spin = QSpinBox()
        self.core_count_spin.setValue(self.gui_vars.core_count)
        self.core_count_spin.setMinimum(1)
        self.core_count_spin.setMaximum(self.gui_vars.phys_core)
        core_layout.addWidget(core_count_label)
        core_layout.addWidget(self.core_count_spin)

        # Batch mode toggle
        batch_layout = QHBoxLayout()
        self.batch_mode_check = QCheckBox("Batch Mode", self)
        self.batch_mode_check.setChecked(self.gui_vars.batch_mode)
        self.batch_mode_check.stateChanged.connect(lambda value: core_libs.gui_funcs.on_state_changed(value, self.gui_vars, 'batch_mode'))
        batch_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        batch_layout.addWidget(self.batch_mode_check)

        # bonemat rotation mode toggle
        bm_rot_layout = QHBoxLayout()
        self.bm_rot_check = QCheckBox("Segmented with RAS Coordinate System", self)
        self.bm_rot_check.setToolTip(
            "This option will rotate bones segmented bones RAS coordinate system.\n"
            "Matching the LPS system used by Bonemat."
        )
        self.bm_rot_check.setChecked(self.gui_vars.bm_rot)
        self.bm_rot_check.stateChanged.connect(lambda value: core_libs.gui_funcs.on_state_changed(value, self.gui_vars, 'bm_rot'))
        bm_rot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bm_rot_layout.addWidget(self.bm_rot_check)

        # INSIGNEO Label
        help_doc_path = os.path.join(self.application_path, 'docs/index.html')
        INSGNO_layout = QHBoxLayout()
        Insigneo_label = QLabel()
        Insigneo_label.setText(f'<a href="file:///{help_doc_path}">HELP</a> | <a href="https://www.sheffield.ac.uk">University of Sheffield</a> | <a href="https://www.sheffield.ac.uk/insigneo">INSIGNEO Institute</a> | <a href="https://ct2s.insigneo.org">CT2S</a>')
        Insigneo_label.setOpenExternalLinks(True)
        Insigneo_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        throbr = core_libs.waitingspinnerwidget.QtWaitingSpinner(self, False, False)
        throbr.setObjectName("throbr")
        throbr.setRoundness(100.0)
        throbr.setMinimumTrailOpacity(5.0)
        throbr.setTrailFadePercentage(85.0)
        throbr.setNumberOfLines(100)
        throbr.setLineLength(4)
        throbr.setLineWidth(1)
        throbr.setInnerRadius(4)
        throbr.setRevolutionsPerSecond(0.5)
        throbr.setColor(QColor("#0078D7"))

        INSGNO_layout.addWidget(throbr)
        INSGNO_layout.addWidget(Insigneo_label)

        # Log Window
        log_layout = QVBoxLayout()
        log_label = QLabel("Log:")
        self.log_text_edit = QTextEdit()
        self.log_text_edit.setReadOnly(True)
        self.log_text_edit.setPlainText("---")
        self.log_text_edit.append(
            "<b>"
            "This software has been designed for research purposes only and has not been reviewed or approved "
            "by medical device regulation bodies."
            "</b>"
        )
        self.log_text_edit.append("---")
        self.log_text_edit.append(
            "PyPeCT2S Copyright(C) 2024 George H. Allison\n"
            "This program comes with ABSOLUTELY NO WARRANTY; for details click HELP.\n"
            "This is free software, and you are welcome to redistribute it "
            "under certain conditions; click HELP for details."
        )
        self.log_text_edit.append("---")
        self.log_text_edit.append("Please ensure you are connected to an ANSYS license server.")
        self.log_text_edit.append(f"Multithreading with maximum {os.cpu_count()} threads.")
        self.log_text_edit.append(
            "ANSYS is best with physical cores, the program has limited selection to use the "
            f"{self.gui_vars.phys_core} physical cores present."
            "\n"
            "ANSYS solvers are CPU intensive, hyperthreading can degrade the solver performance."
        )
        self.log_text_edit.append("---\n")
        self.log_text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.log_text_edit.setMinimumHeight(200)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_text_edit)

        # Batch CPU combo
        batch_cpu_layout = QHBoxLayout()
        batch_cpu_layout.addLayout(core_layout)
        batch_cpu_layout.addStretch()
        batch_cpu_layout.addLayout(bm_rot_layout)
        batch_cpu_layout.addStretch()
        batch_cpu_layout.addLayout(batch_layout)

        mesh_tab = QWidget(self)
        layout = QVBoxLayout()
        mesh_tab.setLayout(layout)

        mat_tab = QWidget(self)
        layout = QVBoxLayout()
        mat_tab.setLayout(layout)

        fem_tab = QWidget(self)
        layout = QVBoxLayout()
        fem_tab.setLayout(layout)

        res_tab = QWidget(self)
        layout = QVBoxLayout()
        res_tab.setLayout(layout)

        self.tab.addTab(mesh_tab, "Meshing")
        self.tab.addTab(mat_tab, "Material")
        self.tab.addTab(fem_tab, "FEM")
        self.tab.addTab(res_tab, "Results")

        self.tab.setTabEnabled(1, True)  # Enable or disable Bonemat Tab, Disabled for Student edition.
        self.tab.setTabEnabled(2, True)  # Enable or disable FEM Tab, Disabled for Student edition.

        main_layout.addLayout(stl_layout)
        main_layout.addLayout(save_layout)
        main_layout.addWidget(drop_widget)
        main_layout.addWidget(self.tab)
        main_layout.addLayout(batch_cpu_layout)
        main_layout.addLayout(log_layout)
        main_layout.addLayout(INSGNO_layout)

        sys.stdout = self.log_text_edit_redirector(self.log_text_edit, sys.stdout)
        sys.stderr = self.log_text_edit_redirector(self.log_text_edit, sys.stderr)

        self.colour_mode()
        self.style_mode()

        self.setWindowTitle("PyPeCT2S")
        self.show()

        self.stl_path_edit.textChanged.connect(lambda: self.check_path_length(self.stl_path_edit))
        self.save_path_edit.textChanged.connect(lambda: self.check_path_length(self.save_path_edit))

        self.core_count_spin.valueChanged.connect(lambda value: core_libs.gui_funcs.on_value_changed(value, self.gui_vars, 'core_count'))

        self.stl_path_edit.textChanged.connect(lambda value: core_libs.gui_funcs.on_value_changed(value, self.gui_vars, 'stl_path'))
        self.save_path_edit.textChanged.connect(lambda value: core_libs.gui_funcs.on_value_changed(value, self.gui_vars, 'save_path'))
        self.gui_vars.app_path = self.application_path
        lambda value: core_libs.gui_funcs.on_value_changed(value, self.gui_vars, 'app_path')

    def discover_scripts(self, drop, group):
        drop.addItem(f"Select {group} script")
        module_path = os.path.join(self.application_path, f"{group}_libs")  # Directory where scripts are stored
        # Find all .py files in the module_path, excluding __init__.py
        for filepath in glob.glob(os.path.join(module_path, "*.py")):
            if os.path.basename(filepath) == "__init__.py":
                continue  # Skip __init__.py
            module_name = os.path.splitext(os.path.basename(filepath))[0]
            spec = importlib.util.spec_from_file_location(module_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, 'get_name'):
                drop.addItem(module.get_name(), module)

    def load_script_content(self, drop, group):
        index = drop.currentIndex()
        module = drop.itemData(index)
        if module and hasattr(module, 'gui_elements'):
            gui_structure = module.gui_elements()

            # Find the index of the tab name in the tab widget
            tab_index = None
            for i in range(self.tab.count()):
                if self.tab.tabText(i) == str(group):
                    tab_index = i
                    break

            # If the tab exists, clear its content and set new content
            if tab_index is not None:
                try:
                    # Create a new QWidget for the content
                    new_content_widget = QWidget()
                    # Use the build_layout function to construct the layout from the gui_structure
                    layout = core_libs.gui_funcs.build_layout(gui_structure)
                    # Set the constructed layout to the new_content_widget
                    new_content_widget.setLayout(layout)

                    # Replace the current widget in the tab with the new_content_widget
                    self.tab.removeTab(tab_index)
                    self.tab.insertTab(tab_index, new_content_widget, str(group))
                except Exception as e:
                    print(f"Error updating {str(group)} tab content: {e}")

    def colour_mode(self):
        # Get the system's default palette
        system_palette = QGuiApplication.palette()

        # Apply the system palette to the application
        self.setPalette(system_palette)

        # Update the application's style to match the system theme
        QCoreApplication.instance().setStyle(QStyleFactory.create('Fusion'))

    def style_mode(self):
        ico_path = (os.path.join(self.application_path, "icons")).replace("\\", "/")
        # Define the stylesheet
        stylesheet = f"""
        QWidget {{
            font-family: 'Segoe UI';
            font-size: 10pt;
        }}
        
        QPushButton {{
            background-color: #0078D7;
            color: #FFF;
            border-style: none;
            padding: 5px 15px;
            border-radius: 2px;
        }}
        
        QPushButton:hover {{
            background-color: #005EA6;
        }}
        
        QPushButton:pressed {{
            background-color: #003C73;
        }}
        
        QPushButton:disabled {{
            background-color: #808080;
            color: #FFF;
        }}
        
        QComboBox {{
            border: 1px solid #808080;
            border-radius: 4px;
            padding: 4px;
        }}
        
        QComboBox::drop-down {{
            border: 0px;
        }}
        
        QComboBox::down-arrow {{
            image: url({ico_path}/arrow_down_g.svg);
            width: 16px;
            height: 16px;
            margin-right: 5px;
        }}
        
        QComboBox QListView {{
            font-size: 10pt;
            border: 0px solid #808080;
            border-radius: 4px;
            padding: 0px;
            outline: none;
        }}
        
        QLineEdit {{
            border: 1px solid #808080;
            border-radius: 2px;
            padding: 5px;
        }}
        
        QLineEdit:focus {{
            border: 1px solid #0078D7;
        }}
        
        QTabWidget::pane {{
            border: 1px solid #808080;
            top: 0px;
            border-bottom-left-radius: 4px;
            border-bottom-right-radius: 4px;
            border-top-right-radius: 4px;
        }}
        
        QTabBar::tab {{
            padding: 4px 8px 4px 8px;
            border: 0px solid #808080;
            border-top-left-radius: 2px;
            border-top-right-radius: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: #0078D7;
            color: #FFF;
        }}
        
        QLabel {{
            margin: 0px;
        }}
        
        QScrollBar:vertical {{
            border: none;
            width: 12px;
            margin: 14px 2px 14px 2px;
            border-radius: 0px;
        }}
        
        QScrollBar::handle:vertical {{	
            background-color: #808080;
            min-height: 10px;
            border-radius: 4px;
        }}
        
        QScrollBar::handle:vertical:hover{{	
            background-color: #0078D7;
        }}
        
        QScrollBar::handle:vertical:pressed {{	
            background-color: #0078D7;
        }}

        QScrollBar::sub-line:vertical {{
            image: url({ico_path}/arrow_up_g.svg);
            border: none;
            height: 14px;
            border-radius: 1px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::sub-line:vertical:hover {{	
            background-color: #0078D7;
            image: url({ico_path}/arrow_up_w.svg);
        }}
        
        QScrollBar::sub-line:vertical:pressed {{
            background-color: #FFF;
            image: url({ico_path}/arrow_up_g.svg);
        }}

        QScrollBar::add-line:vertical {{
            image: url({ico_path}/arrow_down_g.svg);
            border: none;
            height: 14px;
            border-radius: 1px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }}
        
        QScrollBar::add-line:vertical:hover {{	
            background-color: #0078D7;
            image: url({ico_path}/arrow_down_w.svg);
        }}
        
        QScrollBar::add-line:vertical:pressed {{
            background-color: #FFF;
            image: url({ico_path}/arrow_down_g.svg);
        }}
        
        QSpinBox {{
            border: 1px solid #808080;
            border-radius: 2px;
            padding: 4px;
        }}
        
        QSpinBox::up-button {{
            image: url({ico_path}/arrow_up_g.svg);
            width: 12px;
            height: 12px;
            padding: 2px;
        }}
        
        QSpinBox::up-button:hover {{
            background-color: #0078D7;
            image: url({ico_path}/arrow_up_w.svg);
        }}
        
        QSpinBox::down-button {{
            image: url({ico_path}/arrow_down_g.svg);
            width: 12px;
            height: 12px;
            padding: 2px;
        }}
        
        QSpinBox::down-button:hover {{	
            background-color: #0078D7;
            image: url({ico_path}/arrow_down_w.svg);
        }}
        
        QSpinBox:focus {{
            border: 1px solid #0078D7;
        }}
        
        QDoubleSpinBox {{
            border: 1px solid #808080;
            border-radius: 2px;
            padding: 4px;
        }}
        
        QDoubleSpinBox::up-button {{
            image: url({ico_path}/arrow_up_g.svg);
            width: 12px;
            height: 12px;
            padding: 2px;
        }}
        
        QDoubleSpinBox::up-button:hover {{	
            background-color: #0078D7;
            image: url({ico_path}/arrow_up_w.svg);
        }}
        
        QDoubleSpinBox::down-button {{
            image: url({ico_path}/arrow_down_g.svg);
            width: 12px;
            height: 12px;
            padding: 2px;
        }}
        
        QDoubleSpinBox::down-button:hover {{
            background-color: #0078D7;
            image: url({ico_path}/arrow_down_w.svg);
        }}
        
        QDoubleSpinBox:focus {{
            border: 1px solid #0078D7;
        }}
        
        QCheckBox {{
            spacing: 5px;
        }}
        
        QCheckBox::indicator:checked {{
            background-color: #0078D7;
            border: 1px solid #808080;
            border-radius: 4px;
            width: 14px;
            height: 14px;
        }}
        
        QCheckBox::indicator:unchecked {{
            border: 1px solid #808080;
            border-radius: 4px;
            width: 14px;
            height: 14px;
        }}
        """

        # Apply the stylesheet to the application
        QCoreApplication.instance().setStyleSheet(stylesheet)

    def check_path_length(self, line_edit):
        max_length = 248
        text = line_edit.text()
        if len(text) > max_length:
            line_edit.setStyleSheet("QLineEdit { background-color: rgba(255, 0, 0, 0.2); }")
            # Show warning message box
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Warning)
            msg_box.setWindowTitle("Warning")
            msg_box.setText(f"ANSYS supports a {line_edit.placeholderText()}! \n Please select an alternative path.")
            msg_box.exec()
        else:
            pass

    def log_text_edit_redirector(self, log_text_edit, stream):
        return core_libs.texteditredirector.TextEditRedirector(log_text_edit, stream)
