import os
import sys
from io import StringIO

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from matplotlib.ticker import LinearLocator
from scipy.interpolate import griddata
from PyQt5.QtWidgets import QApplication

mpl.use("Qt5Agg")
from run_DebugError import ImagekaError, safe_open


def _load_gif_frame(file_path):
    """Load one whitespace-delimited 2D text frame."""
    try:
        with safe_open(file_path, "r") as file_obj:
            data_str = file_obj.read().replace("D", "E").replace("d", "e")
        data = np.asarray(np.loadtxt(StringIO(data_str), dtype=np.float64))
    except Exception as exc:
        raise ImagekaError(f"Failed to read GIF frame: {file_path}: {exc}") from exc
    if data.ndim != 2 or data.size == 0:
        raise ImagekaError(f"GIF frames must be non-empty 2D arrays: {file_path}")
    return data


def _rectangular_extent(data, config):
    if config.Grid_Ratio == 1:
        x_length = float(config.physical_Z)
        y_length = float(config.physical_R)
    else:
        x_length = float(data.shape[1])
        y_length = float(data.shape[0])

    x_extent = (-x_length / 2, x_length / 2) if config.Grid_center_Z_g == 1 else (0, x_length)
    y_extent = (-y_length / 2, y_length / 2) if config.Grid_center_R_g == 1 else (0, y_length)
    return [x_extent[0], x_extent[1], y_extent[0], y_extent[1]]


def _prepare_display_data(data, config):
    """Return display data and extent for Cartesian or front-view coordinates."""
    if config.cylindrical_g == 0:
        return data, _rectangular_extent(data, config)
    if config.cylindrical_g != 1:
        raise ImagekaError("Invalid view-mode parameter")

    nr, nth = data.shape
    max_radius = float(nr)
    r = np.linspace(0, max_radius, nr)
    theta = np.linspace(0, 2 * np.pi, nth, endpoint=False)
    R, Theta = np.meshgrid(r, theta, indexing="ij")
    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)

    x_cart = np.linspace(-max_radius, max_radius, 500)
    y_cart = np.linspace(-max_radius, max_radius, 500)
    X_cart, Y_cart = np.meshgrid(x_cart, y_cart)
    points = np.column_stack((X.ravel(), Y.ravel()))
    values = data.ravel()
    Z_cart = griddata(points, values, (X_cart, Y_cart), method="linear", fill_value=np.nan)
    mask = np.sqrt(X_cart ** 2 + Y_cart ** 2) > max_radius
    Z_cart[mask] = np.nan
    display_data = np.rot90(Z_cart, k=-1)
    if config.Grid_Ratio == 1:
        extent = [-config.physical_R, config.physical_R,
                  -config.physical_R, config.physical_R]
    else:
        extent = [-max_radius, max_radius, -max_radius, max_radius]
    return display_data, extent


def _get_color_range(data, config):
    if config.use_manual_range:
        vmin = float(config.manual_min)
        vmax = float(config.manual_max)
    else:
        finite_values = data[np.isfinite(data)]
        if finite_values.size == 0:
            raise ImagekaError("The data contains no finite values that can be displayed")
        vmin = float(np.min(finite_values))
        vmax = float(np.max(finite_values))

    if not np.isfinite(vmin) or not np.isfinite(vmax) or vmin > vmax:
        raise ImagekaError("Invalid color range; check the minimum and maximum values")
    if vmin == vmax:
        margin = max(abs(vmin) * 1e-6, 1e-12)
        vmin -= margin
        vmax += margin
    return vmin, vmax


def _set_gif_ticks(ax, config):
    ax.xaxis.set_major_locator(LinearLocator(numticks=max(2, int(config.ticks_x_g))))
    ax.yaxis.set_major_locator(LinearLocator(numticks=max(2, int(config.ticks_y_g))))
    ax.tick_params(axis="both", which="major", pad=4)


def sub_GIF_2D(config):
    """Create a size-configurable GIF from a folder of 2D text array frames."""
    if not os.path.isdir(config.file_path):
        raise ImagekaError(f"Input folder does not exist or is unavailable: {config.file_path}")
    file_list = sorted(
        os.path.join(config.file_path, file_name)
        for file_name in os.listdir(config.file_path)
        if os.path.isfile(os.path.join(config.file_path, file_name))
        and os.path.splitext(file_name)[1].lower() in {".txt", ".dat"}
    )
    if not file_list:
        raise ImagekaError("The input folder contains no usable .txt or .dat 2D array files")
    if not os.path.isdir(config.output_path):
        raise ImagekaError(f"Output folder does not exist or is unavailable: {config.output_path}")
    if config.FPS <= 0 or config.gif_dpi <= 0:
        raise ImagekaError("GIF FPS and DPI must be positive")
    if config.gif_fig_width <= 0 or config.gif_fig_height <= 0:
        raise ImagekaError("GIF output dimensions must be positive")

    print("Using the axial (side) coordinate system" if config.cylindrical_g == 0 else "Using the cylindrical coordinate system")
    print("Using device dimensions" if config.Grid_Ratio else "Using grid dimensions")
    print("Using the global range" if config.use_manual_range else "Using a dynamic range for each frame")
    print("---------")

    gif_path = os.path.join(config.output_path, "output.gif")
    fig, ax = plt.subplots(figsize=(float(config.gif_fig_width), float(config.gif_fig_height)))
    fig.subplots_adjust(left=0.10, right=0.86, bottom=0.12, top=0.90)
    writer = PillowWriter(fps=int(config.FPS))
    writer.setup(fig, gif_path, dpi=int(config.gif_dpi))
    last_shape = None
    try:
        for idx, file_path in enumerate(file_list, start=1):
            data = _load_gif_frame(file_path)
            if config.log_scale_g:
                data = np.log(np.where(data <= 0, 1e-49, data))

            sys.stdout.write(f"Process: {idx}/{len(file_list)} : {os.path.basename(file_path)}\n")
            sys.stdout.flush()
            QApplication.processEvents()

            display_data, extent = _prepare_display_data(data, config)
            vmin, vmax = _get_color_range(data, config)
            ax.clear()
            im = ax.imshow(
                display_data,
                cmap="jet",
                origin="lower",
                extent=extent,
                aspect="equal",
                vmin=vmin,
                vmax=vmax,
            )
            ax.set_xlabel(config.xlabel_g)
            ax.set_ylabel(config.ylabel_g)
            _set_gif_ticks(ax, config)
            if config.show_title_g:
                title = config.title_g.strip() or os.path.basename(file_path)
                ax.set_title(title)

            cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            if config.colorbar_label_g:
                cbar.set_label(config.colorbar_label_g)
            cbar.set_ticks(np.linspace(vmin, vmax, max(1, int(config.ticks_co_g))))
            writer.grab_frame()
            cbar.remove()
            last_shape = data.shape
    finally:
        writer.finish()
        plt.close(fig)

    print("GIF file being saved...")
    print(f"Data shape: {last_shape}")
    print(f"GIF file saved to：{gif_path}")

