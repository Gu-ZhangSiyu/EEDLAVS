class Config:
    def __init__(self):
######################################################
##  Mathematical symbols
##  $z\,[\mathrm{m}]$                       # Physical dimension
##  $\psi\,[\mathrm{W}_{\mathrm{b}}]$       # Magnetic flux
##  $B_z$ [T]                               # Magnetic field
##  $B_{\theta}$ [T]                        # Magnetic field (azimuthal)
##  $E_z$ [V/m]                             # Electric field
##  $j$ [A/m$^{-2}$]                        # Current density
##  $n$ [m$^{-3}$]                          # Plasma density
##  $p\,[\mathrm{Pa}]$                      # Pressure
##  $(j\times B)_r$                         # (j × B)r
##  $(\nabla P)_{r}$                        # (∇ P)r (set mathtext.fontset to stix in the font patch)
##  $\beta$                                 # Beta

######################################################
        # Feature list.
        self.data_handle = 0             # Various data analyses
        self.data_3d_to_2d = 0           # Dimensionality reduction and extraction of 3D field data
        self.data_directory_probe = 0     # Directory-level data inspection
        self.data_nan_check = 0           # Invalid-value check
        self.data_element_compare = 0     # Element distribution comparison
        self.data_field_2d_compare = 0    # 2D field distribution comparison
        self.data_field_compare = 0       # 3D field distribution comparison
        self.dimension_2D = 0            # Display images from 2D planar array files
        self.GIF_2D = 0                  # Export GIFs from 2D planar arrays
        self.single_array_line = 0       # Plot selected data as a line chart
        self.point_Selection = 0         # Time evolution of data at a selected point
        self.part_traj = 0               # Particle trajectories and scatter plot
        self.part_traj_gif = 0           # Particle trajectories and scatter GIF
######################################################
        # General parameters.
        self.input_path = r""
        self.file_path = r""
        self.output_path = r""           # GIFs include a random number to avoid overwriting.
        # ------------------------
        self.NR, self.nth, self.nz = 129, 360, 321   # Cylindrical-coordinate grid.
        self.Grid_Ratio = 1                          # 1: device scale, 0: grid scale.
        self.physical_R = 0.3875                     # Device radius (m): 0.3875.
        self.physical_Z = 2.24                       # Device axial length.
######################################################
        # data_handle parameters.
        self.data_discrete = 0                       # Data dispersion analysis; uses file_path.
        self.file_extreme = 0                        # Single-file extrema; uses input_path.
        self.path_extreme = 0                        # Global path extrema; uses file_path.
        # Data Handle extension parameters.
        self.data_3d_nx = 129                         # 3D field grid points in the X direction.
        self.data_3d_ny = 129                         # 3D field grid points in the Y direction.
        self.data_3d_nz = 257                         # 3D field grid points in the Z direction.
        self.data_3d_plane = "XZ"                    # Slice plane.
        self.data_3d_xz_mode = 1                     # XZ: 0 = radial half-plane, 1 = full plane.
        self.data_3d_z_slice = 0                      # Z index of the XY plane.
        self.data_nan_precision = "float64"         # Precision for NaN checking.
        self.data_element_file_1 = r""
        self.data_element_file_2 = r""
        self.data_element_columns = 4                # Total number of columns in element files.
        self.data_element_x_column = 2               # Starting column for X coordinates (1-based).
        self.data_element_precision = "float64"     # Precision for element comparison.
        self.data_field_2d_file_1 = r""
        self.data_field_2d_file_2 = r""
        self.data_field_2d_nx = 129                  # 2D field comparison X resolution.
        self.data_field_2d_ny = 129                  # 2D field comparison Y resolution.
        self.data_field_2d_precision = "float64"   # Precision for 2D field comparison.
        self.data_field_file_1 = r""
        self.data_field_file_2 = r""
        self.data_field_nx = 129                     # 3D field comparison X resolution.
        self.data_field_ny = 129                     # 3D field comparison Y resolution.
        self.data_field_nz = 257                     # 3D field comparison Z resolution.
        self.data_field_precision = "float64"       # Precision for 3D field comparison.
######################################################        
        # dimension_2D parameters; grid size is detected automatically, so no setting is needed.
        # Supports one- or two-line data.
        self.cylindrical = 0                         # 0: axial (side) view, 1: front view.
        self.log_scale = 0                           # Use a logarithmic scale to amplify differences: 1 = on, 0 = off.
        self.physical_Sin = 8                        # X-axis range for 1D linear data (0 uses the grid range).
        self.Grid_center_R = 1                       # Symmetric R label range: 1 = on, 0 = off.
        self.Grid_center_Z = 1                       # Symmetric Z label range (linear data supports the X axis only): 1 = on, 0 = off.
        self.ticks_x = 5                             # Number of x-axis ticks.
        self.ticks_y = 3                             # Number of y-axis ticks.
        self.ticks_co = 3                            # Number of colorbar ticks.
        self.show_title = 0                          # Show the 2D array image title: 1 = on, 0 = off.
        self.title = r''                             # Image title.
        self.colorbar_label = r''                    # Colorbar label.
        self.Line_1 = r''                            # Line name in two-line mode.
        self.Line_2 = r''
        self.cutoff_x1 = 0                           # Reference-line x position 1 (0 disables it): 0.1169.
        self.cutoff_x2 = 0                           # X position 2: 0.1229.
        self.cutoff_y1 = 0                           # Y position 1: 0.88.
        self.cutoff_y2 = 0                           # Y position 2: 0.58.
        self.color_co = 0                            # Enable x-region coloring: 1 = on, 0 = off.
######################################################
        # GIF_2D parameters.
        self.FPS = 5                                 # GIF frames per second.
        self.cylindrical_g = 0                       # 0: axial (side) view, 1: front view.
        self.Grid_center_R_g = 1                     # GIF radial R-center symmetry: 1 = on, 0 = off.
        self.Grid_center_Z_g = 1                     # GIF axial Z-center symmetry: 1 = on, 0 = off.
        self.ticks_x_g = 5                           # Number of GIF x-axis ticks.
        self.ticks_y_g = 5                           # Number of GIF y-axis ticks.
        self.ticks_co_g = 3                          # Number of GIF colorbar ticks.
        self.show_title_g = 1                        # Show the GIF title: 1 = on, 0 = off.
        self.title_g = r''                           # GIF title; uses the filename when empty.
        self.gif_fig_width = 8.0                     # GIF figure width (inches).
        self.gif_fig_height = 6.0                    # GIF figure height (inches).
        self.gif_dpi = 120                            # GIF output DPI.
        self.log_scale_g = 0                         # Use a logarithmic scale to amplify differences.
        self.xlabel_g = r''                          # X-axis label.
        self.ylabel_g = r''                          # Y-axis label.
        self.colorbar_label_g = r''                  # Colorbar label.
        self.use_manual_range = 0                    # 1: set a global range manually, 0: use a dynamic range.
        self.manual_min = -3.90490252536991e-07      # Data range.
        self.manual_max = 7.4554665005423e-07
######################################################
        # single_array_line
        self.choice_col_ro = 1                       # 1: extract rows, 0: extract columns.
        self.choice_single_num = 90                  # Selected plotting index.
        self.single_ticks_x = 5                      # Number of x-axis ticks.
        self.single_ticks_y = 5                      # Number of y-axis ticks.
        self.single_range_x = 2.24                   # X-axis data range (grid count, physical length, or default grid count).
        self.center_range_x = 1                      # Show the x-axis center: 1 = on.
        self.single_cutoff_x = 0                     # X-axis reference line (0 disables it).
        self.single_cutoff_y = 0                     # Y-axis reference line (0 disables it).
        self.single_cutoff_x_lable = r''             # X-axis reference-line label.
        self.single_cutoff_y_lable = r''             # Y-axis reference-line label.
        self.single_Extreme_value = 1                # Show extrema.
        self.single_title = ''                       # Title.
######################################################
        # point_Selection parameters (the image is not saved).
        self.point_coords = (80, 161)                # Selected point (the first value is nr; default is 129).
        self.cylindrical_point = 0                   # 0: axial (side) view, 1: front view.
        self.ylabel_ps = r'Value'                    # Y-axis (physical quantity) name.
######################################################
        # Static particle trajectory/scatter plot.
        self.paradigm_pt = 0                         # 0: single-particle trajectory, 1: multi-particle scatter (beam plot).
        self.x_columns_pt = 2                        # Column containing X data (if 1, Y is in column 2 and Z in column 3).
        self.R_pt = 0.12                             # Radius. R=0.12 is for trajectory visibility, not the actual device radius; the actual radius is 2 m.
        self.z_min_pt = 0                            # Left-side length.
        self.z_max_pt = 1.7                          # Right-side length.
        self.e_alpha_pt = 0.1                        # Device-shell transparency.
        self.tlw_pt = 2                              # Trajectory line width.
        self.ps_pt = 20                              # Particle marker size.
        self.c_num_pt = 5                            # Number of colorbar ticks.
        self.c_name_pt = ""                          # Colorbar name.
        self.add_field_pt = 1                        # Load background field data.
        self.field_filename = r""                    # Background field file.
        self.field_alpha_pt = 0.1                    # Background field transparency.
        self.field_shape_pt = (129, 257)             # Background field array shape.
        self.x_ticks_num_pt = 9                      # Number of Z-axis ticks (new mapping).
        self.y_ticks_num_pt = 0                      # Number of Y-axis ticks.
        self.z_ticks_num_pt = 3                      # Number of X-axis ticks.
######################################################
        # Particle trajectory/scatter GIF.
        self.paradigm_ptg = 0                        # 0: single-particle trajectory, 1: multi-particle scatter (beam plot).
        self.x_columns_ptg = 2                       # Column containing X data.
        self.fps_ptg = 10                            # Animation frame rate.
        self.plt_dpi_ptg = 100                       # GIF resolution (DPI).
        self.paint_step_ptg = 10                     # Data step. The data buffer can be large enough to exhaust memory.
                                                     # For a single-particle animation this is the sampling step; for a beam animation it is the file-read step.
                                                     # With 3,400 files and 32 GB of RAM, use at least 10; scale proportionally for other data sizes.
        self.add_field_ptg = 0                       # Load background field data.
        self.field_filename_ptg = r""                # Background field data.
        self.field_alpha_ptg = 0.1                   # Background field transparency.
        self.field_shape_ptg = (129, 257)            # Background field array shape.
        self.R_ptg = 0.12                            # Radius. R=0.12 is for trajectory visibility, not the actual device radius; the actual radius is 2 m.
        self.z_min_ptg = 0                           # Left-side length.
        self.z_max_ptg = 1.7                         # Right-side length.
        self.e_alpha_ptg = 0.1                       # Device-shell transparency.
        self.tlw_ptg = 2                             # Trajectory line width.
        self.ps_ptg = 20                             # Particle marker size.
        self.c_num_ptg = 5                           # Number of colorbar ticks.
        self.c_name_ptg = ""                         # Colorbar name.
        self.x_ticks_num_ptg = 9                     # Number of Z-axis ticks (new mapping).
        self.y_ticks_num_ptg = 0                     # Number of Y-axis ticks.
        self.z_ticks_num_ptg = 3                     # Number of X-axis ticks.
