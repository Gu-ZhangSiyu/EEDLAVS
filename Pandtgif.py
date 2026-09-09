import os
import glob
import sys
import imageio
import numpy as np
import matplotlib.cm as cm
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, LinearLocator
from matplotlib.colors import Normalize
from mpl_toolkits.mplot3d import Axes3D
from natsort import natsorted
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

def generate_trajectory_gif(config, field_data=None):
    enable_patch_4dp()
    x, y, z = load_data(config.input_path, config.x_columns_ptg)  # Load all points from one file (one point per row).
    new_x = z
    new_y = y
    new_z = x
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the background field.
    if field_data is not None:
        x_grid = np.linspace(config.z_min_ptg, config.z_max_ptg, field_data.shape[1])
        z_grid = np.linspace(-config.R_ptg, config.R_ptg, field_data.shape[0])
        X_mesh, Z_mesh = np.meshgrid(x_grid, z_grid)
        Y_mesh = np.zeros_like(X_mesh)
        cmap = plt.get_cmap('jet')
        norm = Normalize(vmin=field_data.min(), vmax=field_data.max())
        facecolors = cmap(norm(field_data))
        facecolors[..., 3] = config.e_alpha_ptg
        ax.plot_surface(X_mesh, Y_mesh, Z_mesh, rstride=1, cstride=1, facecolors=facecolors, shade=True)
        mappable = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        # mappable.set_array(field_data)
        mappable.set_array([])
        ticks = np.linspace(field_data.min(), field_data.max(), config.c_num_ptg)
        fig.colorbar(mappable, ax=ax, shrink=0.2, aspect=10, pad=0.1, label=config.c_name_ptg, ticks=ticks)

    # Draw the shell.
    theta = np.linspace(0, 2 * np.pi, 50)
    new_x_vals = np.linspace(config.z_min_ptg, config.z_max_ptg, 50)
    theta_grid, new_x_grid = np.meshgrid(theta, new_x_vals)
    new_y_cyl = config.R_ptg * np.cos(theta_grid)
    new_z_cyl = config.R_ptg * np.sin(theta_grid)
    ax.plot_wireframe(new_x_grid, new_y_cyl, new_z_cyl, color='gray', alpha=0.1)

    # Set axis labels and limits.
    ax.set_xlabel('', labelpad=60)
    ax.set_ylabel('', labelpad=10)
    ax.set_zlabel('', labelpad=10)
    ax.set_xlim(config.z_min_ptg, config.z_max_ptg)
    ax.set_ylim(-config.R_ptg, config.R_ptg)
    ax.set_zlim(-config.R_ptg, config.R_ptg)
    ax.set_box_aspect([config.z_max_ptg - config.z_min_ptg, 2 * config.R_ptg, 2 * config.R_ptg])
    ax.xaxis.set_major_locator(MultipleLocator(0.1))

    # Set the number of ticks.
    if config.x_ticks_num_ptg > 0:
        ax.xaxis.set_major_locator(LinearLocator(config.x_ticks_num_ptg))
    else:
        ax.set_xticks([])
    if config.y_ticks_num_ptg > 0:
        ax.yaxis.set_major_locator(LinearLocator(config.y_ticks_num_ptg))
    else:
        ax.set_yticks([])
    if config.z_ticks_num_ptg > 0:
        ax.zaxis.set_major_locator(LinearLocator(config.z_ticks_num_ptg))
    else:
        ax.set_zticks([])

    # Create an empty line object for displaying the trajectory.
    line, = ax.plot([], [], [], color='blue', lw=config.tlw_ptg, label='Trajectory')
    ax.legend(bbox_to_anchor=(1, 0.7))
    plt.tight_layout()

    # Prepare frame-by-frame GIF output. Unlike feature 2, this writes a temporary GIF
    # in the output path and combines each frame after processing it to avoid exhausting memory.
    total_points = len(new_x)
    output_filename = os.path.join(config.output_path, "output_trajectory.gif")
    writer = imageio.get_writer(output_filename, fps=config.fps_ptg)
    print("Ignore Matplotlib font warnings such as dtype='uint8'.")

    # Update the trajectory.
    for i in range(1, total_points + 1, config.paint_step_ptg):
        line.set_data(new_x[:i], new_y[:i])
        line.set_3d_properties(new_z[:i])
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        writer.append_data(image)
        sys.stdout.write(f"\rProcessing : {i + config.paint_step_ptg - 1}/{total_points} ")  # Update progress after each frame.
        sys.stdout.flush()

    print("\nSaving GIF...")
    writer.close()
    print(f"GIF saved to {output_filename}")
    plt.close(fig)
    disable_patch_4dp()

def generate_gif(file_list, config, field_data=None):
    enable_patch_4dp()
    fig = plt.figure(figsize=(16, 12))
    ax = fig.add_subplot(111, projection='3d')

    # Plot the background field.
    if field_data is not None:
        x_grid = np.linspace(config.z_min_ptg, config.z_max_ptg, field_data.shape[1])
        z_grid = np.linspace(-config.R_ptg, config.R_ptg, field_data.shape[0])
        X_mesh, Z_mesh = np.meshgrid(x_grid, z_grid)
        Y_mesh = np.zeros_like(X_mesh)
        cmap = plt.get_cmap('jet')
        norm = Normalize(vmin=field_data.min(), vmax=field_data.max())
        facecolors = cmap(norm(field_data))
        facecolors[..., 3] = config.e_alpha_ptg
        ax.plot_surface(X_mesh, Y_mesh, Z_mesh, rstride=1, cstride=1, facecolors=facecolors, shade=True)
        mappable = cm.ScalarMappable(norm=norm, cmap=cmap)
        mappable.set_array(field_data)
        ticks = np.linspace(field_data.min(), field_data.max(), config.c_num_ptg)
        fig.colorbar(mappable, ax=ax, shrink=0.2, aspect=10, pad=0.1, label=config.c_name_ptg, ticks=ticks)

    # Draw the shell.
    theta = np.linspace(0, 2 * np.pi, 50)
    new_x_vals = np.linspace(config.z_min_ptg, config.z_max_ptg, 50)
    theta_grid, new_x_grid = np.meshgrid(theta, new_x_vals)
    new_y_cyl = config.R_ptg * np.cos(theta_grid)
    new_z_cyl = config.R_ptg * np.sin(theta_grid)
    ax.plot_wireframe(new_x_grid, new_y_cyl, new_z_cyl, color='gray', alpha=0.1)

    # Set axis labels and limits.
    ax.set_xlabel('', labelpad=60)
    ax.set_ylabel('', labelpad=10)
    ax.set_zlabel('', labelpad=10)
    ax.set_xlim(config.z_min_ptg, config.z_max_ptg)
    ax.set_ylim(-config.R_ptg, config.R_ptg)
    ax.set_zlim(-config.R_ptg, config.R_ptg)
    ax.set_box_aspect([config.z_max_ptg - config.z_min_ptg, 2 * config.R_ptg, 2 * config.R_ptg])
    ax.xaxis.set_major_locator(MultipleLocator(0.1))

    # Set the number of ticks.
    if config.x_ticks_num_ptg > 0:
        ax.xaxis.set_major_locator(LinearLocator(config.x_ticks_num_ptg))
    else:
        ax.set_xticks([])
    if config.y_ticks_num_ptg > 0:
        ax.yaxis.set_major_locator(LinearLocator(config.y_ticks_num_ptg))
    else:
        ax.set_yticks([])
    if config.z_ticks_num_ptg > 0:
        ax.zaxis.set_major_locator(LinearLocator(config.z_ticks_num_ptg))
    else:
        ax.set_zticks([])

    # Plot the scatter points.
    print("Ignore Matplotlib font warnings such as dtype='uint8'.")
    scatter = ax.scatter([], [], [], c='blue', marker='o', s=20, label='Particles')
    ax.legend(bbox_to_anchor=(1, 0.7))
    plt.tight_layout()
    selected_files = file_list[config.paint_step_ptg - 1::config.paint_step_ptg]
    frames = []  # Store each rendered frame.
    total = len(selected_files)
    for i, file in enumerate(selected_files):
        sys.stdout.write(f"\rProcessing : {os.path.basename(file)} ({i + 1}/{total}) ")
        sys.stdout.flush()
        x, y, z = load_data(file, config.x_columns_ptg)
        new_x = z
        new_y = y
        new_z = x
        scatter._offsets3d = (new_x, new_y, new_z)  # Update the scatter object's data.

        # Render the canvas and convert it to an image array.
        fig.canvas.draw()
        image = np.frombuffer(fig.canvas.tostring_rgb(), dtype='uint8')
        image = image.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        frames.append(image)

    print("\nSaving GIF...")
    output_filename = os.path.join(config.output_path, "output_beam.gif")
    imageio.mimsave(output_filename, frames, fps=config.fps_ptg)
    print(f"GIF saved to {output_filename}")
    plt.close(fig)
    disable_patch_4dp()

def pandt_gifka(config):
    plt.rcParams['figure.dpi'] = config.plt_dpi_ptg
    field_data = None
    if config.add_field_ptg:
        print("Loading background field data file:")
        field_data = load_field(config.field_filename_ptg, *config.field_shape_ptg)

    if config.paradigm_ptg == 0:
        print("Displaying a single-particle trajectory animation:")
        generate_trajectory_gif(config, field_data=field_data)
    else:
        print("Displaying a multi-particle beam scatter animation:")
        file_list = natsorted(glob.glob(os.path.join(config.file_path, "*.txt")))  # Get all .txt files and sort them by name.
        generate_gif(file_list, config)
