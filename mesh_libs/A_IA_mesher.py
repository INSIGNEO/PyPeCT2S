"""
================================================================================================================
ANSYS ICEM CFD/APDL Mesher Functions
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

import os
from pathlib import Path
import subprocess
from PyQt6.QtWidgets import QApplication
from ansys.mapdl.core import launch_mapdl
import tempfile
import core_libs
from core_libs import *

# lambda: core_libs.gui_funcs.browse_file_path('Select FEM File Directory', var_ins, 'fname', 'cdb FEM Files (*.cdb);;DB FEM Files (*.db);;All Files (*)', 'ffdir', QApplication.instance().main_window) # for browse_file_path
# lambda: core_libs.gui_funcs.browse_dir_path('Select FEM File Directory', var_ins, 'fname', 'ffdir', QApplication.instance().main_window) # for browse_dir_path
var_ins = core_libs.ansys_vars.MeshVariables()
gui_ins = core_libs.gui_vars.GuiVariables()


def get_name():
    return "ICEM/APDL Mesher"


def gui_elements():
    gui_structure = {
        'type': 'QVBoxLayout',  # Top-level layout
        'items': [
            {
                'type': 'QHBoxLayout',
                'items': [
                    {
                        'type': 'QPushButton',
                        'text': 'Auto Find',
                        'slots': {
                            'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(auto_icem_path, gui_ins.core_count)
                        }
                    },
                    {
                        'type': 'QPushButton',
                        'text': 'Browse',
                        'slots': {
                            'clicked':
                                lambda: core_libs.gui_funcs.browse_file_path('Select ICEM batch File', var_ins, 'icem_path', 'bat Files (*.bat);;All Files (*)', 'icemdir', QApplication.instance().main_window)
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'ICEM Path:'
                    },
                    {
                        'type': 'QLineEdit',
                        'obname': 'icemdir',
                        'placeholder': 'ICEM cfd bat file',
                        'text': var_ins.icem_path,
                        'slots': {
                            'valueChanged': (
                                'icem_path', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'icem_path')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Project Name:'
                    },
                    {
                        'type': 'QLineEdit',
                        'placeholder': 'Project Name',
                        'text': var_ins.proj_name,
                        'slots': {
                            'valueChanged': (
                                'proj_name', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'proj_name')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QHBoxLayout',  # Nested layout
                'items': [
                    {
                        'type': 'QLabel',
                        'text': 'Max Element Size:'
                    },
                    {
                        'type': 'QDoubleSpinBox',
                        'min': 0.00,
                        'max': 10,
                        'value': var_ins.max_element_size,
                        'step': 0.10,
                        'dp': 2,
                        'slots': {
                            'valueChanged': (
                                'max_element_size', var_ins, lambda value: core_libs.gui_funcs.on_value_changed(value, var_ins, 'max_element_size')
                            )
                        }
                    }
                ]
            },
            {
                'type': 'QPushButton',  # Nested layout
                'text': 'Mesh STL File',
                'slots': {
                    'clicked': lambda: core_libs.gui_funcs.gen_thread_worker(run_icem_apdl, gui_ins.core_count)
                }
            }
        ]
    }
    return gui_structure


def rpl_paths(stl_path):
    """
    ==============================================================================
    Handling ICEM commands outside of the script to not cause issues in running
    ==============================================================================
    """

    var_ins.icem_line_3_1 = 'ic_run_application_exec . icemcfd/output-interfaces stl2df {'
    var_ins.icem_line_3_2 = f"{stl_path}"
    match var_ins.stl_type:
        case 'ASCII':
            var_ins.icem_line_3_3 = f' "./tmpdomain0.uns"  -ascii -fam {var_ins.file_name}'
        case 'BINARY':
            var_ins.icem_line_3_3 = f' "./tmpdomain0.uns"  -fam {var_ins.file_name}'
    var_ins.icem_line_3_4 = '}'

    var_ins.icem_line_23_0 = 'ic_uns_update_family_type visible {'
    match var_ins.stl_type:
        case 'ASCII':
            var_ins.icem_line_23_1 = f'{var_ins.file_name}.ASCII'
        case 'BINARY':
            var_ins.icem_line_23_1 = f'{var_ins.file_name}'
    var_ins.icem_line_23_2 = ' ORFN} {TRI_3 !TETRA_4} update 0'

    var_ins.icem_line_25_0 = 'ic_uns_update_family_type visible {'
    match var_ins.stl_type:
        case 'ASCII':
            var_ins.icem_line_25_1 = f'{var_ins.file_name}.ASCII'
        case 'BINARY':
            var_ins.icem_line_25_1 = f'{var_ins.file_name}'
    var_ins.icem_line_25_2 = ' ORFN CREATED_MATERIAL_2} {TRI_3 !TETRA_4} update 0'

    var_ins.icem_line_37_0 = 'ic_save_tetin '
    var_ins.icem_line_37_1 = f'{var_ins.proj_name}.tin'
    var_ins.icem_line_37_2 = ' 0 0 {} {} 0 0 1'

    var_ins.icem_line_41_0 = 'ic_save_unstruct '
    var_ins.icem_line_41_1 = f'{var_ins.proj_name}.uns'
    var_ins.icem_line_41_2 = ' 1 {} {} {}'

    var_ins.icem_line_76_0 = 'ic_save_tetin '
    var_ins.icem_line_76_1 = f'{var_ins.proj_name}.tin'
    var_ins.icem_line_76_2 = ' 0 0 {} {} 0 0 1'

    var_ins.icem_line_79_0 = 'ic_save_unstruct '
    var_ins.icem_line_79_1 = f'{var_ins.proj_name}.uns'
    var_ins.icem_line_79_2 = ' 1 {} {} {}'

    var_ins.icem_line_43_0 = f'ic_save_project_file "{gui_ins.save_path}/{var_ins.proj_name}.prj" '
    var_ins.icem_line_43_1 = '{array\ set\ file_name\ \{ {    catia_dir .} {    parts_dir .} {    domain_loaded 0} {    cart_file_loaded 0} {    cart_file {}} {    domain_saved '
    var_ins.icem_line_43_2 = f'{var_ins.proj_name}.uns'
    var_ins.icem_line_43_3 = '} {    archive {}} {    med_replay {}} {    topology_dir .} {    ugparts_dir .} {    icons {{$env(ICEM_ACN)/lib/ai_env/icons} {$env(ICEM_ACN)/lib/va/EZCAD/icons} {$env(ICEM_ACN)/lib/icons} {$env(ICEM_ACN)/lib/va/CABIN/icons}}} {    tetin '
    var_ins.icem_line_43_4 = f'{var_ins.proj_name}.tin'
    var_ins.icem_line_43_5 = '} {    family_boco {}} {    prism_params ./George.prism_params} {    iges_dir .} {    solver_params_loaded 0} {    attributes_loaded 0} {    project_lock {}} {    attributes {}} {    domain '
    var_ins.icem_line_43_6 = f'{var_ins.proj_name}.uns'
    var_ins.icem_line_43_7 = '} {    domains_dir .} {    settings_loaded 0} {    settings '
    var_ins.icem_line_43_8 = f'{var_ins.proj_name}.prj'
    var_ins.icem_line_43_9 = '} {    blocking {}} {    hexa_replay {}} {    transfer_dir .} {    mesh_dir .} {    family_topo {}} {    gemsparts_dir .} {    family_boco_loaded 0} {    tetin_loaded 1} {    project_dir .} {    topo_mulcad_out {}} {    solver_params {}} \} array\ set\ options\ \{ {    expert 1} {    remote_path {}} {    tree_disp_quad 2} {    tree_disp_pyra 0} {    evaluate_diagnostic 0} {    histo_show_default 1} {    select_toggle_corners 0} {    remove_all 0} {    keep_existing_file_names 0} {    record_journal 0} {    edit_wait 0} {    face_mode all} {    select_mode all} {    med_save_emergency_tetin 1} {    user_name George} {    diag_which all} {    uns_warn_if_display 500000} {    bubble_delay 1000} {    external_num 1} {    tree_disp_tri 2} {    apply_all 0} {    temporary_directory {}} {    flood_select_angle 0} {    home_after_load 1} {    project_active 0} {    histo_color_by_quality_default 1} {    undo_logging 1} {    tree_disp_hexa 0} {    histo_solid_default 1} {    host_name DESKTOP-NPPP69T} {    xhidden_full 1} {    replay_internal_editor 1} {    editor {}} {    mouse_color orange} {    clear_undo 1} {    remote_acn {}} {    remote_sh csh} {    tree_disp_penta 0} {    n_processors 1} {    remote_host {}} {    save_to_new 0} {    quality_info Quality} {    tree_disp_node 0} {    med_save_emergency_mesh 1} {    redtext_color red} {    tree_disp_line 0} {    select_edge_mode 0} {    use_dlremote 0} {    max_mesh_map_size 1024} {    show_tris 1} {    remote_user {}} {    enable_idle 0} {    auto_save_views 1} {    max_cad_map_size 512} {    display_origin 0} {    uns_warn_user_if_display 1000000} {    detail_info 0} {    win_java_help 0} {    show_factor 1} {    boundary_mode all} {    clean_up_tmp_files 1} {    auto_fix_uncovered_faces 1} {    med_save_emergency_blocking 1} {    max_binary_tetin 0} {    tree_disp_tetra 0} \} array\ set\ disp_options\ \{ {    uns_dualmesh 0} {    uns_warn_if_display 500000} {    uns_normals_colored 0} {    uns_icons 0} {    uns_locked_elements 0} {    uns_shrink_npos 0} {    uns_node_type None} {    uns_icons_normals_vol 0} {    uns_bcfield 0} {    backup Solid/wire} {    uns_nodes 0} {    uns_only_edges 0} {    uns_surf_bounds 0} {    uns_wide_lines 0} {    uns_vol_bounds 0} {    uns_displ_orient Triad} {    uns_orientation 0} {    uns_directions 0} {    uns_thickness 0} {    uns_shell_diagnostic 0} {    uns_normals 0} {    uns_couplings 0} {    uns_periodicity 0} {    uns_single_surfaces 0} {    uns_midside_nodes 1} {    uns_shrink 100} {    uns_multiple_surfaces 0} {    uns_no_inner 0} {    uns_enums 0} {    uns_disp Wire} {    uns_bcfield_name {}} {    uns_color_by_quality 0} {    uns_changes 0} {    uns_cut_delay_count 1000} \} {set icon_size1 24} {set icon_size2 35} {set thickness_defined 0} {set solver_type 1} {set solver_setup -1} array\ set\ prism_values\ \{ {    n_triangle_smoothing_steps 5} {    min_smoothing_steps 6} {    first_layer_smoothing_steps 1} {    new_volume {}} {    height 0} {    prism_height_limit 0} {    interpolate_heights 0} {    n_tetra_smoothing_steps 10} {    do_checks {}} {    delete_standalone 1} {    ortho_weight 0.50} {    max_aspect_ratio {}} {    ratio_max {}} {    incremental_write 0} {    total_height 0} {    use_prism_v10 0} {    intermediate_write 1} {    delete_base_triangles {}} {    ratio_multiplier {}} {    verbosity_level 1} {    refine_prism_boundary 1} {    max_size_ratio {}} {    triangle_quality {}} {    max_prism_angle 180} {    tetra_smooth_limit 0.30000001} {    max_jump_factor 5} {    use_existing_quad_layers 0} {    layers 3} {    fillet 0.1} {    into_orphan 0} {    init_dir_from_prev {}} {    blayer_2d 0} {    do_not_allow_sticking {}} {    top_family {}} {    law exponential} {    min_smoothing_val 0.1} {    auto_reduction 0} {    max_prism_height_ratio 0} {    stop_columns 1} {    stair_step 1} {    smoothing_steps 12} {    side_family {}} {    min_prism_quality 0.0099999998} {    ratio 1.2} \} {set aie_current_flavor {}} array\ set\ vid_options\ \{ {    auxiliary 0} {    show_name 0} {    inherit 1} {    default_part GEOM} {    new_srf_topo 1} {    DelPerFlag 0} {    composite_tolerance 1.0} {    replace 0} {    same_pnt_tol 1e-4} {    tdv_axes 1} {    vid_mode 0} {    DelBlkPerFlag 0} \} {set savedTreeVisibility {geomNode 2 geomSurfNode 2 meshNode 1 mesh_subsetNode 2 meshShellNode 2 meshTriNode 2 meshVolumeNode 0 meshTetraNode 0 partNode 2 part-CREATED_MATERIAL_2 2 part-'
    match var_ins.stl_type:
        case 'ASCII':
            var_ins.icem_line_40_10 = f'{var_ins.file_name}.ASCII'
        case 'BINARY':
            var_ins.icem_line_40_10 = f'{var_ins.file_name}'
    var_ins.icem_line_43_11 = ' 2}} {set last_view {rot {0 0 0 1} scale {13.5742371737 13.5742371737 13.5742371737} center {38.77415 -3.3241 -197.3125} pos {0 0 0}}} array\ set\ cut_info\ \{ {    active 0} \} array\ set\ hex_option\ \{ {    default_bunching_ratio 2.0} {    floating_grid 0} {    project_to_topo 0} {    n_tetra_smoothing_steps 20} {    sketching_mode 0} {    trfDeg 1} {    wr_hexa7 0} {    hexa_projection_mode 0} {    smooth_ogrid 0} {    find_worst 1-3} {    hexa_verbose_mode 0} {    old_eparams 0} {    uns_face_mesh_method uniform_quad} {    multigrid_level 0} {    uns_face_mesh one_tri} {    check_blck 0} {    proj_limit 0} {    check_inv 0} {    project_bspline 0} {    hexa_update_mode 1} {    default_bunching_law BiGeometric} {    worse_criterion Quality} \} array\ set\ saved_views\ \{ {    views {}} \}} {ICEM CFD}'

    var_ins.icem_line_87_0 = f'ic_save_project_file "{gui_ins.save_path}/{var_ins.proj_name}.prj" '
    var_ins.icem_line_87_1 = '{array\ set\ file_name\ \{ {    catia_dir .} {    parts_dir .} {    domain_loaded 0} {    cart_file_loaded 0} {    cart_file {}} {    domain_saved '
    var_ins.icem_line_87_2 = f'{var_ins.proj_name}.uns'
    var_ins.icem_line_87_3 = '} {    archive {}} {    med_replay {}} {    topology_dir .} {    ugparts_dir .} {    icons {{$env(ICEM_ACN)/lib/ai_env/icons} {$env(ICEM_ACN)/lib/va/EZCAD/icons} {$env(ICEM_ACN)/lib/icons} {$env(ICEM_ACN)/lib/va/CABIN/icons}}} {    tetin '
    var_ins.icem_line_87_4 = f'{var_ins.proj_name}.tin'
    var_ins.icem_line_87_5 = '} {    family_boco '
    var_ins.icem_line_87_6 = f'{var_ins.proj_name}.fbc'
    var_ins.icem_line_87_7 = '} {    prism_params ./George.prism_params} {    iges_dir .} {    solver_params_loaded 1} {    attributes_loaded 1} {    project_lock {}} {    attributes '
    var_ins.icem_line_87_8 = f'{var_ins.proj_name}.atr'
    var_ins.icem_line_87_9 = '} {    domain '
    var_ins.icem_line_87_10 = f'{var_ins.proj_name}.uns'
    var_ins.icem_line_87_11 = '} {    domains_dir .} {    settings_loaded 0} {    settings '
    var_ins.icem_line_87_12 = f'{var_ins.proj_name}.prj'
    var_ins.icem_line_87_13 = '} {    blocking {}} {    hexa_replay {}} {    transfer_dir .} {    mesh_dir .} {    family_topo {}} {    gemsparts_dir .} {    family_boco_loaded 1} {    tetin_loaded 1} {    project_dir .} {    topo_mulcad_out {}} {    solver_params '
    var_ins.icem_line_87_14 = f'{var_ins.proj_name}.par'
    var_ins.icem_line_87_15 = '} \} array\ set\ options\ \{ {    expert 1} {    remote_path {}} {    tree_disp_quad 2} {    tree_disp_pyra 0} {    evaluate_diagnostic 0} {    histo_show_default 1} {    select_toggle_corners 0} {    remove_all 0} {    keep_existing_file_names 0} {    record_journal 0} {    edit_wait 0} {    face_mode all} {    select_mode all} {    med_save_emergency_tetin 1} {    user_name George} {    diag_which all} {    uns_warn_if_display 500000} {    bubble_delay 1000} {    external_num 1} {    tree_disp_tri 2} {    apply_all 0} {    temporary_directory {}} {    flood_select_angle 0} {    home_after_load 1} {    project_active 0} {    histo_color_by_quality_default 1} {    undo_logging 1} {    tree_disp_hexa 0} {    histo_solid_default 1} {    host_name DESKTOP-NPPP69T} {    xhidden_full 1} {    replay_internal_editor 1} {    editor {}} {    mouse_color orange} {    clear_undo 1} {    remote_acn {}} {    remote_sh csh} {    tree_disp_penta 0} {    n_processors 1} {    remote_host {}} {    save_to_new 0} {    quality_info Quality} {    tree_disp_node 0} {    med_save_emergency_mesh 1} {    redtext_color red} {    tree_disp_line 0} {    select_edge_mode 0} {    use_dlremote 0} {    max_mesh_map_size 1024} {    show_tris 1} {    remote_user {}} {    enable_idle 0} {    auto_save_views 1} {    max_cad_map_size 512} {    display_origin 0} {    uns_warn_user_if_display 1000000} {    detail_info 0} {    win_java_help 0} {    show_factor 1} {    boundary_mode all} {    clean_up_tmp_files 1} {    auto_fix_uncovered_faces 1} {    med_save_emergency_blocking 1} {    max_binary_tetin 0} {    tree_disp_tetra 0} \} array\ set\ disp_options\ \{ {    uns_dualmesh 0} {    uns_warn_if_display 500000} {    uns_normals_colored 0} {    uns_icons 0} {    uns_locked_elements 0} {    uns_shrink_npos 0} {    uns_node_type None} {    uns_icons_normals_vol 0} {    uns_bcfield 0} {    backup Solid/wire} {    uns_nodes 0} {    uns_only_edges 0} {    uns_surf_bounds 0} {    uns_wide_lines 0} {    uns_vol_bounds 0} {    uns_displ_orient Triad} {    uns_orientation 0} {    uns_directions 0} {    uns_thickness 0} {    uns_shell_diagnostic 0} {    uns_normals 0} {    uns_couplings 0} {    uns_periodicity 0} {    uns_single_surfaces 0} {    uns_midside_nodes 1} {    uns_shrink 100} {    uns_multiple_surfaces 0} {    uns_no_inner 0} {    uns_enums 0} {    uns_disp Wire} {    uns_bcfield_name {}} {    uns_color_by_quality 0} {    uns_changes 0} {    uns_cut_delay_count 1000} \} {set icon_size1 24} {set icon_size2 35} {set thickness_defined 0} {set solver_type 1} {set solver_setup 1} array\ set\ prism_values\ \{ {    n_triangle_smoothing_steps 5} {    min_smoothing_steps 6} {    first_layer_smoothing_steps 1} {    new_volume {}} {    height 0} {    prism_height_limit 0} {    interpolate_heights 0} {    n_tetra_smoothing_steps 10} {    do_checks {}} {    delete_standalone 1} {    ortho_weight 0.50} {    max_aspect_ratio {}} {    ratio_max {}} {    incremental_write 0} {    total_height 0} {    use_prism_v10 0} {    intermediate_write 1} {    delete_base_triangles {}} {    ratio_multiplier {}} {    verbosity_level 1} {    refine_prism_boundary 1} {    max_size_ratio {}} {    triangle_quality {}} {    max_prism_angle 180} {    tetra_smooth_limit 0.30000001} {    max_jump_factor 5} {    use_existing_quad_layers 0} {    layers 3} {    fillet 0.1} {    into_orphan 0} {    init_dir_from_prev {}} {    blayer_2d 0} {    do_not_allow_sticking {}} {    top_family {}} {    law exponential} {    min_smoothing_val 0.1} {    auto_reduction 0} {    max_prism_height_ratio 0} {    stop_columns 1} {    stair_step 1} {    smoothing_steps 12} {    side_family {}} {    min_prism_quality 0.0099999998} {    ratio 1.2} \} {set aie_current_flavor {}} array\ set\ vid_options\ \{ {    auxiliary 0} {    show_name 0} {    inherit 1} {    default_part GEOM} {    new_srf_topo 1} {    DelPerFlag 0} {    composite_tolerance 1.0} {    replace 0} {    same_pnt_tol 1e-4} {    tdv_axes 1} {    vid_mode 0} {    DelBlkPerFlag 0} \} {set savedTreeVisibility {geomNode 2 geomSurfNode 2 meshNode 1 mesh_subsetNode 2 meshShellNode 2 meshTriNode 2 meshVolumeNode 0 meshTetraNode 0 partNode 2 part-CREATED_MATERIAL_2 2 part-'
    match var_ins.stl_type:
        case 'ASCII':
            var_ins.icem_line_87_16 = f'{var_ins.file_name}.ASCII'
        case 'BINARY':
            var_ins.icem_line_87_16 = f'{var_ins.file_name}'
    var_ins.icem_line_87_17 = ' 2}} {set last_view {rot {0 0 0 1} scale {13.5742371737 13.5742371737 13.5742371737} center {38.77415 -3.3241 -197.3125} pos {0 0 0}}} array\ set\ cut_info\ \{ {    active 0} \} array\ set\ hex_option\ \{ {    default_bunching_ratio 2.0} {    floating_grid 0} {    project_to_topo 0} {    n_tetra_smoothing_steps 20} {    sketching_mode 0} {    trfDeg 1} {    wr_hexa7 0} {    hexa_projection_mode 0} {    smooth_ogrid 0} {    find_worst 1-3} {    hexa_verbose_mode 0} {    old_eparams 0} {    uns_face_mesh_method uniform_quad} {    multigrid_level 0} {    uns_face_mesh one_tri} {    check_blck 0} {    proj_limit 0} {    check_inv 0} {    project_bspline 0} {    hexa_update_mode 1} {    default_bunching_law BiGeometric} {    worse_criterion Quality} \} array\ set\ saved_views\ \{ {    views {}} \}} {ICEM CFD}'

    var_ins.icem_line_88_1 = 'ic_exec {'
    var_ins.icem_line_88_2 = f'{((Path(var_ins.icem_path).parents[1]).joinpath("icemcfd", "output-interfaces", "ansys.exe"))}'
    var_ins.icem_line_88_3 = '} '
    var_ins.icem_line_88_4 = f'-dom {var_ins.proj_name}.uns -atr "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.fbc" -par "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.par" "{gui_ins.save_path}/{var_ins.proj_name}.inp" -use_blocks -make_comp -no_bar -no_shell'


def find_icem_path():
    for folder, subfolders, files in os.walk(var_ins.root_dir):
        for file in files:
            if file == 'icemcfd.bat':
                return os.path.abspath(os.path.join(folder, file))
    return None


def auto_icem_path():
    try:
        try:
            var_ins.icem_path = find_icem_path()
            print(f'Path to icemcfd.bat found: {var_ins.icem_path}')
            core_libs.gui_funcs.update_line_edit(var_ins.icem_path, 'icemdir', QApplication.instance().main_window)
            #var_ins.icem_ansys_path = (((Path(var_ins.icem_path).parents[1]).joinpath('icemcfd', 'output-interfaces', 'ansys.exe')))
        except:
            print('Standard Auto-Find Method, failed. Falling back to alternate method.')
            base_ansys_dir = 'C:/Program Files/Ansys Inc/'
            directories = [os.path.join(base_ansys_dir, d) for d in os.listdir(base_ansys_dir) if os.path.isdir(os.path.join(base_ansys_dir, d))]
            directories = [d for d in directories if d.startswith(os.path.join(base_ansys_dir, 'v'))]
            for d in directories:
                paths = glob.glob(os.path.join(d, 'icemcfd', 'win64_amd', 'bin', 'icemcfd.bat'))
                if paths:
                    var_ins.icem_path = paths[0]
                    print(f'Path to icemcfd.bat found: {var_ins.icem_path}')
                    core_libs.gui_funcs.update_line_edit(var_ins.icem_path, 'icemdir', QApplication.instance().main_window)
                    #var_ins.icem_ansys_path = (((Path(var_ins.icem_path).parents[1]).joinpath('icemcfd', 'output-interfaces', 'ansys.exe')))

    except Exception as e:
        print(e)
        print('Path to icemcfd.bat not found.\n Please manually set the path.')


def update_icem_commands(stl_path):
    var_ins.icem_commands = [
        f'ic_chdir "{gui_ins.save_path}"',
        'ic_csystem_set_current global',
        f'ic_file_is_ascii "{stl_path}"',
        f'{var_ins.icem_line_3_1}"{var_ins.icem_line_3_2}"{var_ins.icem_line_3_3}{var_ins.icem_line_3_4}',
        'ic_empty_tetin',
        'ic_geo_import_mesh ./tmpdomain0.uns 1 1',
        'ic_boco_solver',
        'ic_boco_clear_icons',
        'ic_set_global geo_cad 0.05 toler',
        f'ic_set_meshing_params global 0 gref 1.0 gmax {var_ins.max_element_size} gfast 0 gedgec 0.2 gnat 0 gcgap 1 gnatref 10',
        'ic_set_meshing_params surface_global 0 mesh_type 0 mesh_method 1 simple_offset 0 bunch_respect 0 protect_line 0 bound_smooth 0 block_mapping 0.2 adjust_nodes_max 0.0 proj_surf 1 surf_sizes 0 ign_size 0.05 try_harder 1 impr_level 1 mesh_dormant 0 smooth_dormant 0 max_area 0.0 max_length 0.0 min_angle 0.0 max_nodes 0 max_elements 0 merge_surfs 1 mapped_method 1 free_bunch 0 shrinkwrap_nsmooth 5 shrinkwrap_projfactor 0.1 snorm 1 quadratic 0',
        'ic_set_meshing_params global 0 gfast 0 gedgec 0.2',
        'ic_set_global geo_cad 0.05 toler',
        'ic_save_tetin temp_tetra.tin',
        'ic_run_tetra temp_tetra.tin ./tetra_mesh.uns run_cutter 1 delete_auto 1 run_smoother 0 fix_holes 1 n_processors 1 in_process 1 auto_vol 1 log ./tetra_cmd.log',
        'ic_geo_set_modified 1',
        f'{var_ins.icem_line_23_0}{var_ins.icem_line_23_1}{var_ins.icem_line_23_2}',
        'ic_boco_solver',
        f'{var_ins.icem_line_25_0}{var_ins.icem_line_25_1}{var_ins.icem_line_25_2}',
        'ic_boco_clear_icons',
        'ic_uns_diagnostic diag_type single quiet 1',
        'ic_smooth_elements map all upto 0.4 iterations 5 fix_families {} n_processors 1 smooth TRI_3 float TETRA_4 laplace 1',
        'ic_smooth_elements map all upto 0.4 iterations 5 prism_warp_weight 0.5 fix_families {} n_processors 1 smooth TETRA_4 float PENTA_6 freeze TRI_3',
        'ic_smooth_elements map all upto 0.4 iterations 5 prism_warp_weight 0.5 fix_families {} metric Quality n_processors 1 smooth TETRA_4 smooth TRI_3 float PENTA_6',
        'ic_geo_set_modified 1',
        'ic_delete_empty_parts',
        f'ic_chdir "{gui_ins.save_path}"',
        'ic_delete_empty_parts',
        f'{var_ins.icem_line_37_0}{var_ins.icem_line_37_1}{var_ins.icem_line_37_2}',
        f'ic_rename {var_ins.proj_name}.uns {var_ins.proj_name}.uns.bak',
        'ic_uns_check_duplicate_numbers',
        'ic_uns_renumber_all_elements 1 1',
        f'{var_ins.icem_line_41_0}{var_ins.icem_line_41_1}{var_ins.icem_line_41_2}',
        'ic_uns_set_modified 1',
        f'{var_ins.icem_line_43_0}{var_ins.icem_line_43_1}{var_ins.icem_line_43_2}{var_ins.icem_line_43_3}{var_ins.icem_line_43_4}{var_ins.icem_line_43_5}{var_ins.icem_line_43_6}{var_ins.icem_line_43_7}{var_ins.icem_line_43_8}{var_ins.icem_line_43_9}{var_ins.icem_line_43_10}{var_ins.icem_line_43_11}',
        'ic_boco_solver',
        'ic_boco_solver {Ansys Fluent}',
        'ic_solution_set_solver {Ansys Fluent} 1',
        'ic_boco_solver {Ansys Fluent}',
        'ic_solver_mesh_info {Ansys Fluent}',
        f'ic_boco_save "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.fbc"',
        f'ic_boco_save_atr "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.atr"',
        f'ic_param_save "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.par"',
        'ic_boco_solver',
        'ic_boco_solver {Ansys Fluent}',
        'ic_solution_set_solver {Ansys Fluent} 1',
        f'ic_boco_save "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.fbc"',
        f'ic_boco_save_atr "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.atr"',
        f'ic_param_save "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.par"',
        'ic_uns_thickness_exists_mesh',
        'ic_uns_thickness_exists_mesh',
        'ic_uns_thickness_exists_mesh',
        'ic_uns_thickness_exists_mesh',
        'ic_boco_unload',
        f'ic_boco_load "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.fbc"',
        'ic_boco_solver Ansys',
        f'ic_param_load "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.par"',
        'ic_param_set_all {:ansys_product:ST,EXPASS 0 :ansys_product:FL:FLDATA5,MACH 1 :ansys_product:TH,timestep 0 :def_3_TH_1,inopr 0 :ansys_product:FL:FLDATA5,PTOT 1 :ansys_product,save_opt 1 :def_3_ST_1,type 200 :def_3_FL_1,inopr 0 :contact:real_contact3,r10 0.0 :contact:real_contact3,r11 1.0 :ansys_product:FL:FLDATA5,SPHT 0 :def_2_TH_1,type 0 :contact:real_contact3,r12 1.0 :contact:real_contact3,r13 0.0 :def_2_ST_1:kop181,kop1 -1 :contact:real_contact3,r14 0.0 :ansys_product:FL:FLDATA5,DENS 1 :def_2_ST_1:kop181,kop2 -1 :contact:real_contact3,r15 1.0 :ansys_product:FL:FLDATA5,RESI 0 :def_2_ST_1:kop181,kop3 0 :contact:real_contact3,r16 0.0 :def_2_ST_1:kop181,kop4 -1 :contact:real_contact3,r17 1.0 :def_2_ST_1:kop181,kop5 -1 :contact:real_contact3,r18 0.5 :def_2_ST_1:kop181,kop6 -1 :contact:real_contact3,r20 1.0 :contact:real_contact3,r19 0.0 :contact:real_contact3,r21 1.0 :contact:real_contact3,r3 1.0 :ansys_product:FL:FLDATA3,ENDS 1E-02 :contact:real_contact3,r22 0.0 :contact:real_contact3,r4 0.1 :contact:real_contact3,r23 0.01 :contact:real_contact3,r5 0.0 :def_3_TH_1,real None :contact:real_contact3,r6 0.0 :contact:real_contact3,r25 0.0 :contact:real_contact3,r7 0.0 :contact:kop_contact3,kop1 0 :contact:real_contact3,r8 0.0 :contact:kop_contact3,kop2 0 :ansys_product:ST,mod_norm 0 :contact:real_contact3,r9 1.0E20 :contact:kop_contact3,kop3 -1 :contact:kop_contact3,kop4 0 :ansys_product:FL:FLDATA5,EVIS 1 :ansys_product:TH,BETAD 0.0 :contact:kop_contact3,kop5 0 :contact:kop_contact3,kop6 -1 :ansys_product:FL:FLDATA1,TURB 0 :contact:kop_contact3,kop7 0 :contact:kop_contact3,kop8 0 :contact:kop_contact3,kop9 0 :def_2_ST_2,type 200 :def_0_ST_3,real None :def_1_ST_1:kop188,kop1 0 :def_1_ST_1:kop188,kop2 0 :def_1_ST_1:kop188,kop3 0 :ansys_product:ST,DMPRAT 0.02 :def_1_ST_1:kop188,kop4 0 :ansys_product:FL:FLDATA14,NOMI 293.0 :def_1_ST_1:kop188,kop5 -1 :ansys_product:TH,anal_type None :ansys_product:TH,solv_type SPARSE :def_1_ST_1:kop188,kop6 0 :ansys_product:ST,mod_solv LANB :ansys_product:FL:FLDATA1,IVSH 0 :def_3_ST_2,real None :ansys_product:FL:FLDATA13,SFTS 0 :ansys_product:TH,DELTIM1 0 :def_3_TH_2:kop90,kop1 0 :def_3_ST_1:kop195,kop1 -1 :ansys_product:TH,DELTIM2 0 :def_3_TH_2:kop90,kop2 -1 :def_3_ST_1:kop195,kop2 0 :global,DOMEGA 0 :def_3_TH_2:kop90,kop3 -1 :def_3_ST_1:kop195,kop3 -1 :def_3_TH_2:kop90,kop4 -1 :def_1_ST_1,sec None :ansys_product:FL:FLDATA13,COND 0 :def_3_ST_1:kop195,kop4 -1 :ansys_product,opt0 1 :def_3_TH_2:kop90,kop5 -1 :def_3_ST_1:kop195,kop5 -1 :ansys_product,opt1 {} :def_3_TH_2:kop90,kop6 -1 :def_3_TH_1:kop70,kop1 -1 :def_3_ST_1:kop195,kop6 -1 :ansys_product,opt2 {} :def_3_TH_1:kop70,kop2 0 :ansys_product:TH,DELTIM 1.0 :ansys_product,opt3 {} :def_3_TH_1:kop70,kop3 -1 :ansys_product,opt4 {} :def_3_TH_1:kop70,kop4 0 :def_3_ST_2:kop95,kop1 0 :def_3_TH_1:kop70,kop5 -1 :def_3_ST_2:kop95,kop2 -1 :def_3_TH_1:kop70,kop6 -1 :def_3_ST_2:kop95,kop3 -1 :def_3_ST_2:kop95,kop4 -1 :def_3_ST_2:kop95,kop5 0 :def_3_ST_2:kop92,kop1 -1 :def_3_ST_2:kop95,kop6 0 :def_3_ST_2:kop92,kop2 -1 :def_3_ST_1:kop185,kop1 -1 :def_3_ST_2:kop92,kop3 -1 :ansys_product:FL:FLDATA1,SPEC 0 :def_0_TH_3,type 0 :def_3_ST_1:kop185,kop2 0 :def_3_ST_2:kop92,kop4 -1 :def_3_ST_1:kop185,kop3 -1 :def_3_ST_2:kop92,kop5 0 :def_3_ST_1:kop185,kop4 0 :def_3_ST_2:kop92,kop6 0 :def_3_ST_1:kop185,kop5 -1 :contact:kop_contact3,kop10 0 :def_3_ST_1:kop185,kop6 0 :ansys_product:FL:FLDATA3,TEMP 1E-08 :contact:kop_contact3,kop11 0 :def_2_ST_1:kop41,kop1 0 :contact:kop_contact3,kop12 0 :def_2_ST_1:kop41,kop2 0 :def_2_ST_1:kop41,kop3 -1 :ansys_product:ST,TIMINT 1 :def_1_ST_1:kop10,kop1 -1 :def_2_ST_1:kop41,kop4 0 :ansys_product:FL:FLDATA3,ENKE 1E-02 :def_1_ST_1:kop10,kop2 0 :def_2_ST_1:kop41,kop5 0 :def_3_TH_2,type 200 :ansys_product:FL:FLDATA5,YPLU 0 :def_1_ST_1:kop10,kop3 0 :def_2_ST_1:kop41,kop6 0 :def_1_ST_1:kop10,kop4 -1 :def_1_ST_1:kop10,kop5 -1 :def_3_ST_1:kop65,kop1 0 :ansys_product:FL:FLDATA5,ECON 1 :def_1_ST_1:kop10,kop6 -1 :def_3_ST_1:kop65,kop2 -1 :def_3_ST_1:kop65,kop3 -1 :def_1_FL_1,real None :def_3_ST_1:kop65,kop4 -1 :ansys_product:FL:FLDATA5,RDFL 0 :ansys_product:FL:FLDATA5,SFTS 0 :def_3_ST_1:kop65,kop5 0 :ansys_product:FL:FLDATA6,OUTP BNOW :def_3_ST_1:kop65,kop6 0 :def_1_FL_1:kop116,kop1 0 :ansys_product:ST,AUTOTS -1 :def_1_FL_1:kop116,kop2 0 :def_1_FL_1:kop116,kop3 -1 :ansys_product:FL:FLDATA5,COND 1 :ansys_product:ST,ALPHAD 0.0 :def_1_FL_1:kop116,kop4 0 :def_1_FL_1:kop116,kop5 0 :def_1_FL_1:kop116,kop6 0 :ansys_product:FL,flag 0 :ansys_product,lab_EH_ST_0 n :ansys_product:ST,NSUBST 1 :ansys_product:FL:FLDATA16,BETA 1.0E15 :def_1_ST_1:kop52,kop1 0 :def_1_ST_1:kop52,kop2 -1 :def_1_ST_1:kop52,kop3 0 :def_0_ST_3,inopr 0 :def_2_FL_1:kop141,kop1 0 :def_1_ST_1:kop52,kop4 0 :def_2_FL_1:kop141,kop2 -1 :def_1_ST_1:kop52,kop5 -1 :def_2_FL_1:kop141,kop3 0 :def_1_ST_1:kop52,kop6 -1 :def_2_FL_1:kop141,kop4 0 :def_1_ST_1,real None :ansys_product:FL:FLDATA1,FLOW 1 :def_2_FL_1:kop141,kop5 -1 :ansys_product:FL:FLDATA6,ITER 1 :def_2_ST_2:kop93,kop1 -1 :ansys_product,lab_EH_TH_0 n :def_2_FL_1:kop141,kop6 -1 :def_2_FL_1,type 200 :def_2_ST_2:kop93,kop2 -1 :ansys_product,lab_EH_TH_1 n :def_2_ST_2:kop93,kop3 -1 :def_3_ST_2:kop194,kop1 -1 :def_2_ST_2:kop93,kop4 0 :def_3_ST_2:kop194,kop2 0 :def_2_ST_2:kop93,kop5 0 :def_3_ST_2:kop194,kop3 -1 :def_3_ST_1:kop45,kop1 0 :def_2_ST_2:kop93,kop6 0 :ansys_product:ST,NSUBST1 0 :ansys_product:FL:FLDATA5,TTOT 1 :def_3_ST_2:kop194,kop4 -1 :def_3_ST_1:kop45,kop2 0 :ansys_product:ST,NSUBST2 0 :def_3_ST_2:kop194,kop5 -1 :def_3_ST_1:kop45,kop3 -1 :def_3_ST_2:kop194,kop6 -1 :def_3_ST_1:kop45,kop4 0 :def_3_ST_1:kop45,kop5 0 :def_3_ST_1:kop45,kop6 0 :def_2_TH_1:kop57,kop1 -1 :def_3_FL_1,real None :ansys_product:TH,NLGEOM OFF :def_2_TH_1:kop57,kop2 0 :def_3_ST_2:kop187,kop1 -1 :def_2_TH_1:kop57,kop3 -1 :def_3_ST_2:kop187,kop2 -1 :def_2_TH_1:kop57,kop4 -1 :def_3_ST_2:kop187,kop3 -1 :ansys_product:ST,solv_tol 1.0E-08 :def_2_TH_1:kop57,kop5 -1 :def_3_ST_2:kop187,kop4 0 :def_2_TH_1:kop57,kop6 -1 :def_3_ST_2:kop187,kop5 -1 :def_3_ST_2:kop187,kop6 0 :ansys_product,lab_TH_ST_0 n :def_2_ST_1:kop63,kop1 0 :def_2_ST_1:kop63,kop2 0 :def_3_EH_2,type 200 :def_2_ST_1:kop63,kop3 0 :def_2_ST_1,type 200 :ansys_product,type1 ST :def_2_ST_1:kop63,kop4 -1 :ansys_product,type2 TH :def_2_ST_1:kop63,kop5 0 :def_2_ST_1:kop63,kop6 0 :def_3_ST_1,real None :ansys_product,exit_save SOLU :def_1_ST_2,inopr 0 :def_2_TH_1,real None :global,DOMEGA_XYZ {0 0 0} :def_0_TH_3:kop71,kop1 -1 :def_0_TH_3:kop71,kop2 -1 :ansys_product:ST,mod_expec 0 :def_0_TH_3:kop71,kop3 0 :def_0_TH_3:kop71,kop4 0 :ansys_product,kimg 1 :def_0_TH_3:kop71,kop5 -1 :def_0_TH_3:kop71,kop6 -1 :ansys_product:ST,KBC 1 :def_3_FL_1:kop142,kop1 0 :def_1_ST_2,type 0 :def_0_ST_3:kop21,kop1 0 :def_3_FL_1:kop142,kop2 -1 :ansys_product:FL:FLDATA13,VISC 0 :def_0_ST_3:kop21,kop2 0 :def_3_FL_1:kop142,kop3 0 :def_0_ST_3:kop21,kop3 0 :def_3_FL_1:kop142,kop4 0 :def_0_ST_3:kop21,kop4 -1 :def_3_FL_1:kop142,kop5 -1 :ansys_product:FL:FLDATA5,PCOE 1 :def_0_ST_3:kop21,kop5 -1 :def_2_ST_1:kop43,kop1 -1 :ansys_product:ST,solv_mult 1.0 :def_3_FL_1:kop142,kop6 -1 :def_1_ST_1,inopr 0 :def_0_ST_3:kop21,kop6 -1 :def_2_ST_1:kop43,kop2 -1 :def_2_ST_1:kop43,kop3 0 :ansys_product:TH,solv_tol 1.0E-08 :global,ACEL 0 :ansys_product:FL:FLDATA5,DEBG 1 :def_2_ST_1:kop43,kop4 0 :def_2_ST_1:kop43,kop5 0 :def_2_ST_1:kop43,kop6 0 :def_0_TH_3,inopr 0 :def_2_ST_2,real None :contact,1 {} :def_2_ST_1:kop143,kop1 -1 :def_2_ST_1:kop143,kop2 0 :def_3_TH_1,type 200 :ansys_product:FL:FLDATA5,TAUW 0 :ansys_product:ST,DELTIM 1.0 :ansys_product:FL:FLDATA1,TRAN 0 :def_2_ST_1:kop143,kop3 0 :def_2_ST_2,inopr 0 :def_2_ST_1:kop143,kop4 0 :def_3_ST_1:kop64,kop1 0 :def_2_ST_1:kop143,kop5 0 :def_3_ST_1:kop64,kop2 -1 :def_2_ST_1:kop143,kop6 0 :ansys_product,coupled 0 :def_3_ST_1:kop64,kop3 -1 :ansys_product:FL:FLDATA5,STRM 1 :def_3_ST_1:kop64,kop4 -1 :def_3_ST_1:kop64,kop5 0 :ansys_product:TH,NSUBST1 0 :def_3_ST_1:kop64,kop6 0 :ansys_product:TH,NSUBST2 0 :def_0_ST_3,type 0 :ansys_product:FL:FLDATA1,SFTS 0 :ansys_product:FL:FLDATA5,HFLM 1 :ansys_product:TH,KBC 1 :global,OMEGA_XYZ {0 0 0} :ansys_product:FL:FLDATA1,VOF 0 :def_3_EH_2,inopr 0 :ansys_product:ST,TIME 1.0 :def_2_ST_1,inopr 0 :def_1_ST_2:kop189,kop1 0 :def_1_ST_1:kop4,kop1 -1 :def_1_ST_2:kop189,kop2 0 :ansys_product:FL:FLDATA1,COMP 0 :def_1_ST_1:kop4,kop2 0 :def_1_ST_2:kop189,kop3 -1 :def_3_ST_2,type 200 :def_1_ST_1:kop4,kop3 -1 :def_1_ST_2:kop189,kop4 0 :ansys_product:FL:FLDATA5,VISC 1 :def_1_ST_1:kop4,kop4 -1 :def_1_ST_2:kop189,kop5 -1 :ansys_product:TH,TIME 1.0 :def_1_ST_1:kop4,kop5 -1 :def_1_ST_2:kop189,kop6 0 :ansys_product:FL:FLDATA5,HFLU 1 :def_1_ST_1:kop4,kop6 0 :ansys_product:FL:FLDATA3,PRES 1E-08 :def_0_TH_3,real None :ansys_product:ST,freq2 1E+08 :def_3_ST_2,inopr 0 :ansys_product:FL:FLDATA5,EMD 1 :def_1_ST_1:kop44,kop1 -1 :ansys_product:ST,HROPT FULL :def_1_ST_1:kop44,kop2 0 :def_1_ST_1:kop44,kop3 -1 :def_1_ST_1:kop44,kop4 -1 :def_3_EH_2:kop119,kop1 1 :def_3_EH_2:kop120,kop1 1 :ansys_product:FL:FLDATA5,SUMF 10 :def_1_ST_1:kop44,kop5 -1 :def_3_TH_2,real None :def_3_EH_2:kop119,kop2 -1 :def_3_EH_2:kop120,kop2 -1 :ansys_product:FL:FLDATA3,VX 1E-02 :def_1_ST_1:kop44,kop6 0 :def_3_EH_2:kop119,kop3 -1 :def_3_EH_2:kop120,kop3 -1 :ansys_product:FL:FLDATA3,VY 1E-02 :def_3_EH_2:kop119,kop4 0 :def_3_EH_2:kop120,kop4 0 :ansys_product:FL:FLDATA3,VZ 1E-02 :def_3_EH_2:kop119,kop5 0 :def_3_EH_2:kop120,kop5 0 :def_3_EH_2:kop119,kop6 -1 :def_3_EH_2:kop120,kop6 -1 :def_3_ST_2:kop186,kop1 -1 :def_3_ST_1,inopr 0 :def_3_ST_2:kop186,kop2 -1 :ansys_product:FL:FLDATA15,REFE 1.0135E05 :def_3_ST_2:kop186,kop3 -1 :ansys_product,lab_EH_FL_0 n :def_3_ST_2:kop186,kop4 0 :ansys_product,lab_EH_FL_1 n :def_3_ST_2:kop186,kop5 -1 :def_3_ST_2:kop186,kop6 0 :def_1_ST_2,sec None :def_1_FL_1,type 200 :global,OMEGA 0 :ansys_product:FL:FLDATA17,COMP 1.4 :def_1_FL_1,inopr 0 :ansys_product:TH,TIMINT 1 :ansys_product:ST,NLGEOM OFF :def_1_ST_1:kop24,kop1 0 :ansys_product:ST,timestep 0 :def_3_TH_2:kop87,kop1 0 :ansys_product:FL:FLDATA14,BULK 293.0 :def_1_ST_1:kop24,kop2 0 :global,OMEGA_SPIN 0 :def_3_TH_2:kop87,kop2 -1 :def_1_ST_1:kop24,kop3 0 :ansys_product:ST,anal_type None :ansys_product:ST,solv_type SPARSE :ansys_product:ST,mod_n 1 :def_3_TH_2:kop87,kop3 -1 :def_1_ST_1:kop180,kop1 -1 :def_2_FL_1,real None :def_1_ST_1:kop24,kop4 -1 :def_3_TH_2:kop87,kop4 -1 :def_1_ST_1:kop180,kop2 0 :def_1_ST_1:kop24,kop5 -1 :def_3_TH_2:kop87,kop5 -1 :def_1_ST_1:kop180,kop3 -1 :def_1_ST_1:kop24,kop6 0 :def_3_TH_2:kop87,kop6 -1 :def_1_ST_1:kop180,kop4 -1 :def_1_ST_1:kop180,kop5 -1 :ansys_product:TH,solv_mult 1.0 :def_1_ST_1:kop180,kop6 -1 :ansys_product:TH,AUTOTS -1 :ansys_product:TH,ALPHAD 0.0 :def_1_ST_1,type 0 :ansys_product,exit_opt 0 :def_2_TH_1,inopr 0 :ansys_product,lab_FL_ST_0 n :ansys_product:FL:FLDATA13,SPHT 0 :ansys_product:TH,NSUBST 1 :ansys_product:FL:FLDATA1,ALE 0 :ansys_product:ST,NUMEXP ALL :ansys_product:ST,freq 0.0 :ansys_product:FL:FLDATA13,DENS 0 :ansys_product:ST,mod_ce 0 :ansys_product:ST,DELTIM1 0 :ansys_product:ST,BETAD 0.0 :ansys_product:FL:FLDATA1,TEMP 0 :ansys_product:FL:FLDATA14,TTOT 293.0 :ansys_product:ST,DELTIM2 0 :global,ACEL_XYZ {0 0 0} :def_2_FL_1,inopr 0 :ansys_product:FL:FLDATA1,SWRL 0 :def_3_EH_2,real None :ansys_product:FL:FLDATA5,LMD 1 :def_2_ST_1,real None :def_3_FL_1,type 200 :def_3_TH_2,inopr 0 :ansys_product,proc_n 1 :ansys_product,lab_FL_TH_0 n :ansys_product,lab_FL_TH_1 n}',
        f'ic_param_save "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.par"',
        'ic_boco_unload',
        'ic_param_set_all {}',
        f'ic_param_load "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.par" 0',
        f'ic_boco_load_atr "{gui_ins.save_path}/{var_ins.proj_name}.fluentAnsys.atr"',
        'ic_boco_clear_icons',
        'ic_delete_empty_parts',
        f'{var_ins.icem_line_76_0}{var_ins.icem_line_76_1}{var_ins.icem_line_76_2}',
        f'ic_rename {var_ins.proj_name}.uns {var_ins.proj_name}.uns.bak',
        'ic_uns_check_duplicate_numbers',
        f'{var_ins.icem_line_79_0}{var_ins.icem_line_79_1}{var_ins.icem_line_79_2}',
        'ic_uns_set_modified 1',
        'ic_boco_solver',
        'ic_boco_solver Ansys',
        'ic_solution_set_solver Ansys 1',
        f'ic_boco_save {var_ins.proj_name}.fbc',
        f'ic_boco_save_atr {var_ins.proj_name}.atr',
        f'ic_param_save {var_ins.proj_name}.par',
        f'ic_param_save {var_ins.proj_name}.par',
        f'{var_ins.icem_line_87_0}{var_ins.icem_line_87_1}{var_ins.icem_line_87_2}{var_ins.icem_line_87_3}{var_ins.icem_line_87_4}{var_ins.icem_line_87_5}{var_ins.icem_line_87_6}{var_ins.icem_line_87_7}{var_ins.icem_line_87_8}{var_ins.icem_line_87_9}{var_ins.icem_line_87_10}{var_ins.icem_line_87_11}{var_ins.icem_line_87_12}{var_ins.icem_line_87_13}{var_ins.icem_line_87_14}{var_ins.icem_line_87_15}{var_ins.icem_line_87_16}{var_ins.icem_line_87_17}',
        f'{var_ins.icem_line_88_1}{var_ins.icem_line_88_2}{var_ins.icem_line_88_3}{var_ins.icem_line_88_4}',
        'exit'
    ]


def run_icem(stl_path):
    try:
        update_icem_commands(stl_path)
        var_ins.icem_commands = "\n".join(var_ins.icem_commands)  # Combine commands into a single string
        with open(f"{gui_ins.save_path}/temp_icem_script.rpl", "w") as file:
            file.write(var_ins.icem_commands)  # Save commands to temporary file
        auto = subprocess.run([var_ins.icem_path, "-batch", "-script", f"{gui_ins.save_path}/temp_icem_script.rpl"], capture_output=True, text=True, check=True)  # Run ICEM CFD with the script
        print(auto.stdout)
        print(auto.stderr)
        for file in var_ins.files_to_remove:
            try:
                pass
                # Try to remove temporary files
                os.remove(f'{gui_ins.save_path}/{file}')
            except OSError:
                # If the file does not exist or cannot be removed, ignore the error
                pass
        print('ICEM CFD meshing complete!')
    except subprocess.CalledProcessError as e:
        print(f"Command '{e.cmd}' returned non-zero exit status {e.returncode}.")
        print("Error:", e.stderr)
    except Exception as e:
        print(f'Error: {e}')


def apdl_mesh():
    mapdl = launch_mapdl(nproc=gui_ins.core_count, loglevel="WARNING", print_com=True, cleanup_on_exit=True)
    try:
        # File > Read Input From > Patient00X.inp
        mapdl.cwd(f"{gui_ins.save_path}/")
        mapdl.input(f"{var_ins.proj_name}.inp")

        # Preprocessor > Element type > Add/Edit/Delete > Add -> Solid -> 10 node 187 > ok > close
        mapdl.prep7()
        mapdl.et(2, 187)

        # NSEL, ALL
        mapdl.nsel("ALL")

        # EMODIF, ALL, TYPE, 2
        mapdl.emodif("ALL", "TYPE", 2)

        # ESEL, ALL
        mapdl.esel("ALL")

        # EMID, ADD, ALL
        mapdl.emid("ADD", "ALL")

        # File > save as > Patient00X.db
        mapdl.finish()
        mapdl.save(f"{var_ins.proj_name}.db")

        # Archive Model > write > save Patient00X.cdb
        mapdl.cdwrite("ALL", f"{var_ins.proj_name}", "cdb", f"{var_ins.proj_name}", "iges", "BLOCKED")

        mapdl.exit()
        print('MESHING COMPLETE!\n *.cdb files have been saved')
    except Exception as e:
        mapdl.exit()
        print(e)
        print('ANSYS APDL meshing failed!')


def run_icem_apdl():

    try:
        core_libs.stl_checks.STLChecks(gui_ins.stl_path)  # Check the STL file is valid
    except Exception as e:
        print(
            f"Error: {e} - Check you have set a valid STL and save file path.\n"
            "Could not perform STL checks, proceed with caution."
        )

    match gui_ins.bm_rot:
        case True:
            try:
                stl_mesh = core_libs.gui_funcs.rotate_stl_180_z(gui_ins.stl_path)
                with tempfile.NamedTemporaryFile(delete=False, dir=gui_ins.save_path, suffix=".stl") as temp_file:
                    stl_mesh.save(temp_file.name)
                    stl_path = temp_file.name.replace("\\", "/")
            except Exception as e:
                print(
                    f"Error: {e}\n"
                    "- Check you have set a valid STL and save file path.\n"
                    "- Could not rotate the STL file, please check the file is not corrupted."
                )
        case False:
            stl_path = gui_ins.stl_path

    var_ins.stl_type = core_libs.gui_funcs.check_stl_file_type(stl_path)
    var_ins.file_name_ext = (os.path.basename(stl_path))
    var_ins.file_name = (os.path.splitext(os.path.basename(stl_path))[0]).upper()

    try:
        rpl_paths(stl_path)
    except Exception as e:
        print(f'Error: {e}')

    try:
        run_icem(stl_path)
    except Exception as e:
        print(f'Error: {e}\n ANSYS ICEM has failed to run please check you have files in the correct location')

    if temp_file:
        try:
            os.remove(temp_file.name)
        except OSError:
            pass
        except Exception as e:
            print(f'Error deleting temporary file: {e}')

    try:
        apdl_mesh()
    except Exception as e:
        print(e)
        print('ANSYS APDL meshing failed!')
