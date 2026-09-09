import sys
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, LinearLocator
from matplotlib.colors import Normalize
import matplotlib as mpl
mpl.use("Qt5Agg")
from plotconfig import enable_patch_4dp, disable_patch_4dp

def load_data(filename, x_columns):
    try:
        data = np.loadtxt(filename)
        if data.shape[1] < 3:
            raise ValueError("(x, y, z) data must be in columns 1, 2, and 3")
        x, y, z = data[:, x_columns - 1], data[:, x_columns], data[:, x_columns + 1]
        return x, y, z
    except ValueError as ve:
        print(f"Data reading error: {ve}")
        sys.exit(1)

def load_field(filename, xx, yy):
    try:
        data = np.loadtxt(filename)
        field_values = data[:, 0]
        if field_values.size != xx * yy:
            xyxy = xx * yy
            raise ValueError(f"Field data row count mismatch: expected {xyxy}, got {field_values.size} rows")
        field_array = field_values.reshape((xx, yy))
        print("Field data loaded successfully")
        return field_array
    except ValueError as ve:
        print(f"Data reading error: {ve}")
        sys.exit(1)

def plot_particles_tra(config):
    field_data = None
    if config.add_field_pt:
        print("Loading background field data file")
        field_data = load_field(config.field_filename, *config.field_shape_pt)
    if config.paradigm_pt == 0:
        print("Displaying a single-particle trajectory plot")
    else:
        print("Displaying a multi-particle beam scatter plot")
    x, y, z = load_data(config.input_path, config.x_columns_pt)

    enable_patch_4dp()
    new_x = z       # Remap the axis.
    new_y = x
    new_z = y
    fig = plt.figure(figsize=(16, 12))               # Figure size.
    ax = fig.add_subplot(111, projection='3d')      # Create a 3D plot.

    # Plot the background field.
    if field_data is not None:
        # Build the grid.
        x_grid = np.linspace(config.z_min_pt, config.z_max_pt, field_data.shape[1])     # new_x axis (original z axis): from z_min to z_max.
        z_grid = np.linspace(-config.R_pt, config.R_pt, field_data.shape[0])            # new_z axis (original x axis): from -R to R.
        X_mesh, Z_mesh = np.meshgrid(x_grid, z_grid)
        Y_mesh = np.zeros_like(X_mesh)
        cmap = plt.get_cmap('jet')
        norm = Normalize(vmin=field_data.min(), vmax=field_data.max())
        facecolors = cmap(norm(field_data))         # Generate the color array and adjust the alpha channel.
        facecolors[..., 3] = config.field_alpha_pt                # The alpha setting is ineffective; force alpha (possibly a library-version issue).
        surf = ax.plot_surface(X_mesh, Y_mesh, Z_mesh, rstride=1, cstride=1, facecolors=facecolors, shade=True)
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array(field_data)
        ticks = np.linspace(field_data.min(), field_data.max(), config.c_num_pt)
        fig.colorbar(mappable, ax=ax, shrink=0.2, aspect=10, pad=0.08, label=config.c_name_pt, ticks=ticks)

    # Plot the particle data.
    if config.paradigm_pt == 1:
        ax.scatter(new_x, new_y, new_z, c='blue', marker='o', s=config.ps_pt, label='Particles')
    else:
        ax.plot(new_x, new_y, new_z, label='Particle trajectory', color='blue', lw=config.tlw_pt)

    ax.set_xlabel('', labelpad=60)
    ax.set_ylabel('', labelpad=10)
    ax.set_zlabel('', labelpad=10)
    ax.set_xlim(config.z_min_pt, config.z_max_pt)
    ax.set_ylim(-config.R_pt, config.R_pt)
    ax.set_zlim(-config.R_pt, config.R_pt)
    ax.set_box_aspect([config.z_max_pt - config.z_min_pt, 2 * config.R_pt, 2 * config.R_pt])
    ax.xaxis.set_major_locator(MultipleLocator(0.1))

    # Set the number of ticks.
    if config.x_ticks_num_pt > 0:
        ax.xaxis.set_major_locator(LinearLocator(config.x_ticks_num_pt))
    else:
        ax.set_xticks([])
    if config.y_ticks_num_pt > 0:
        ax.yaxis.set_major_locator(LinearLocator(config.y_ticks_num_pt))
    else:
        ax.set_yticks([])
    if config.z_ticks_num_pt > 0:
        ax.zaxis.set_major_locator(LinearLocator(config.z_ticks_num_pt))
    else:
        ax.set_zticks([])

    # Draw the cylindrical shell.
    theta = np.linspace(0, 2 * np.pi, 50)
    new_x_vals = np.linspace(config.z_min_pt, config.z_max_pt, 50)
    theta_grid, new_x_grid = np.meshgrid(theta, new_x_vals)
    new_y_cyl = config.R_pt * np.cos(theta_grid)
    new_z_cyl = config.R_pt * np.sin(theta_grid)
    ax.plot_wireframe(new_x_grid, new_y_cyl, new_z_cyl, color='gray', alpha=config.e_alpha_pt)
    ax.legend(bbox_to_anchor=(1, 0.7))
    plt.tight_layout()
    plt.show()
    disable_patch_4dp()
