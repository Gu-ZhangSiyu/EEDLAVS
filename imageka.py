import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator
from matplotlib.ticker import MaxNLocator
from matplotlib.ticker import ScalarFormatter
from scipy.interpolate import griddata
mpl.use("Qt5Agg")      # Tell Matplotlib to use the active Qt5 backend.
from run_DebugError import safe_open
from plotconfig import enable_patch_2dp, disable_patch_2dp, enable_patch_4dp, disable_patch_4dp


def sub_dimension_2D(config):
    file_list = [config.input_path]
    for file_path in file_list:
        # Read the file.
        with safe_open(file_path, 'r') as file:
            lines = file.readlines()
        ny = len(lines)
        nx = len(lines[0].split())

        # Process and plot the data.
        if ny == 1 or nx == 1:
            # Enable the grid globally.
            plt.figure(figsize=(12, 8))
            mpl.rcParams['axes.grid'] = True
            mpl.rcParams['grid.linestyle'] = '--'
            mpl.rcParams['grid.linewidth'] = 0.8  # Grid-line width.
            mpl.rcParams['grid.alpha'] = 0.8  # Grid-line transparency.
            mpl.rcParams['lines.linewidth'] = 2.5  # Line width.
            print(f"Detected linear data with length {max(ny, nx)}")
            enable_patch_2dp()
            data = []
            for line in lines:
                values = line.split()
                data.extend([float(value.replace('D', 'E')) for value in values])
            data = np.array(data)
            if config.log_scale:
                print("Applying logarithmic transform")
                data = np.log(np.where(data <= 0, 1e-49, data))
            # Generate a new physical x-axis.
            n = data.size
            if config.physical_Sin != 0:
                if config.Grid_center_Z == 1:
                    x = np.linspace(-config.physical_Sin/2, config.physical_Sin/2, n)
                else:
                    x = np.linspace(0, config.physical_Sin, n)
                plt.plot(x, data)
            else:
                plt.plot(data)

            ax = plt.gca()
            ax.xaxis.set_major_locator(MaxNLocator(config.ticks_x))
            ax.yaxis.set_major_locator(MaxNLocator(config.ticks_y))

            # Add dashed reference-line markers.
            if config.cutoff_x1 != 0:
                plt.axvline(x=config.cutoff_x1, color='b', linestyle='--', linewidth=2, label=f'R={config.cutoff_x1}[m]')
            if config.cutoff_x2 != 0:
                plt.axvline(x=config.cutoff_x2, color='b', linestyle=':', linewidth=2, label=f'R={config.cutoff_x2}[m]')
            if config.cutoff_y1 != 0:
                plt.axhline(y=config.cutoff_y1, color='r', linestyle='--', linewidth=2, label=f'β={config.cutoff_y1}')
            if config.cutoff_y2 != 0:
                plt.axhline(y=config.cutoff_y2, color='r', linestyle=':', linewidth=2, label=f'β={config.cutoff_y2}')
            # Color the region.
            if config.color_co == 1 and config.cutoff_x1 != 0 and config.cutoff_x2 != 0:
                plt.axvspan(config.cutoff_x1, config.cutoff_x2, color='gray', alpha=0.2, label="Wave penetration")
            if (config.cutoff_x1 != 0 and config.cutoff_x2 != 0) or \
                    (config.cutoff_y1 != 0 and config.cutoff_y2 != 0):
                plt.legend()
            disable_patch_2dp()

        elif nx == 2:
            plt.figure(figsize=(12, 8))
            mpl.rcParams['axes.grid'] = True
            mpl.rcParams['grid.linestyle'] = '--'
            mpl.rcParams['grid.linewidth'] = 0.8    # Grid-line width.
            mpl.rcParams['grid.alpha'] = 0.8        # Grid-line transparency.
            mpl.rcParams['lines.linewidth'] = 2.5   # Line width.
            print(f"Detected two-column linear data with length {ny}; multi-line plots do not support logarithmic transforms")
            enable_patch_2dp()
            data = []
            for line in lines:
                values = line.split()
                data.append([float(value.replace('D', 'E')) for value in values])
            data = np.array(data)
            ax = plt.gca()
            ax.xaxis.set_major_locator(MaxNLocator(config.ticks_x))
            ax.yaxis.set_major_locator(MaxNLocator(config.ticks_y))
            plt.plot(data[:, 0], data[:, 1])

            # Use scientific notation for the y-axis range (replace the formatter manually,
            # otherwise this setting has no effect).
            fmt_y = ScalarFormatter(useMathText=True)
            fmt_y.set_powerlimits((0, 0))
            ax.yaxis.set_major_formatter(fmt_y)

            # Add dashed reference-line markers.
            if config.cutoff_x1 != 0:
                plt.axvline(x=config.cutoff_x1, color='b', linestyle='--', linewidth=2, label=f'R={config.cutoff_x1}[m]')
            if config.cutoff_x2 != 0:
                plt.axvline(x=config.cutoff_x2, color='b', linestyle=':', linewidth=2, label=f'R={config.cutoff_x2}[m]')
            if config.cutoff_y1 != 0:
                plt.axhline(y=config.cutoff_y1, color='r', linestyle='--', linewidth=2, label=f'β={config.cutoff_y1}')
            if config.cutoff_y2 != 0:
                plt.axhline(y=config.cutoff_y2, color='r', linestyle=':', linewidth=2, label=f'β={config.cutoff_y2}')
            # Color the region.
            if config.color_co == 1 and config.cutoff_x1 != 0 and config.cutoff_x2 != 0:
                plt.axvspan(config.cutoff_x1, config.cutoff_x2, color='gray', alpha=0.2, label="Wave penetration")
            if (config.cutoff_x1 != 0 and config.cutoff_x2 != 0) or \
                    (config.cutoff_y1 != 0 and config.cutoff_y2 != 0):
                plt.legend()
            disable_patch_2dp()
        elif nx == 3:
            plt.figure(figsize=(12, 8)) 
            mpl.rcParams['axes.grid'] = True
            mpl.rcParams['grid.linestyle'] = '--'
            mpl.rcParams['grid.linewidth'] = 0.8    # Grid-line width.
            mpl.rcParams['grid.alpha'] = 0.8        # Grid-line transparency.
            mpl.rcParams['lines.linewidth'] = 2.5   # Line width.
            print(f"Detected three-column linear data with length {ny}; multi-line plots do not support logarithmic transforms")
            enable_patch_2dp()
            data = []
            for line in lines:
                values = line.split()
                data.append([float(value.replace('D', 'E')) for value in values])
            data = np.array(data)
            ax = plt.gca()
            ax.xaxis.set_major_locator(MaxNLocator(config.ticks_x))
            ax.yaxis.set_major_locator(MaxNLocator(config.ticks_y))
            plt.plot(data[:, 0], data[:, 1], label=config.Line_1, linestyle='--', marker='o')  # First line.
            plt.plot(data[:, 0], data[:, 2], label=config.Line_2, linestyle='-', marker='x')  # Second line.
            plt.legend()  # Show the legend.
            disable_patch_2dp()
        else:
            print(f"Detected 2D planar data with shape ({nx}, {ny})")
            print("Using device dimensions" if config.Grid_Ratio == 1 else "Using grid dimensions")
            enable_patch_4dp()      # Enable four-decimal formatting in the patch.
            plt.figure(figsize=(16, 8)) 
            if config.cylindrical == 0:
                data = np.zeros((ny, nx))
                for i, line in enumerate(lines):
                    if not line.strip():
                        continue
                    values = line.split()
                    for j in range(nx):
                        data[i, j] = float(values[j].replace('D', 'E'))
                if config.Grid_Ratio == 1:
                    if config.Grid_center_R == 1 and config.Grid_center_Z == 1:
                        extent = [-config.physical_Z / 2, config.physical_Z / 2, -config.physical_R / 2, config.physical_R / 2]
                    elif config.Grid_center_R == 1:
                        extent = [0, config.physical_Z, -config.physical_R/2, config.physical_R/2]
                    elif config.Grid_center_Z == 1:
                        extent = [-config.physical_Z/2, config.physical_Z/2, 0, config.physical_R]
                    else:
                        extent = [0, config.physical_Z, 0, config.physical_R]
                else:
                    x_extent = (-nx / 2, nx / 2) if config.Grid_center_Z == 1 else (0, nx)
                    y_extent = (-ny / 2, ny / 2) if config.Grid_center_R == 1 else (0, ny)
                    extent = [x_extent[0], x_extent[1], y_extent[0], y_extent[1]]
                plt.imshow(data, cmap='jet', origin='lower', extent=extent, aspect='equal')

                if config.Grid_Ratio == 1:
                    if config.physical_R == 0.3857:
                        cbar = plt.colorbar(label=config.colorbar_label, shrink=0.3)
                        cbar.set_ticks(np.linspace(cbar.vmin, cbar.vmax, config.ticks_co))
                    else:
                        cbar = plt.colorbar(label=config.colorbar_label, shrink=0.35)
                        cbar.set_ticks(np.linspace(cbar.vmin, cbar.vmax, config.ticks_co))
                else:
                    cbar = plt.colorbar(label=config.colorbar_label, shrink=0.5)
                    cbar.set_ticks(np.linspace(cbar.vmin, cbar.vmax, config.ticks_co))

                # Use scientific notation for the colorbar.
                formatter = ScalarFormatter(useMathText=True)
                formatter.set_powerlimits((0, 0))
                cbar.formatter = formatter
                cbar.update_ticks()

                # Place major ticks evenly on [xmin, xmax], including both endpoints.
                ax = plt.gca()
                ax.xaxis.set_major_locator(LinearLocator(numticks=config.ticks_x))
                ax.yaxis.set_major_locator(LinearLocator(numticks=config.ticks_y))

                # Adjust major ticks: pad = label-to-axis distance, width = tick width,
                # length = tick-line length.
                ax.tick_params(axis='both', which='major', pad=8, width=1.2, length=8)

                disable_patch_4dp()     # Disable four-decimal formatting in the patch.
            elif config.cylindrical == 1:
                print("Detected cylindrical-coordinate data; processing...")
                enable_patch_4dp()  # Enable four-decimal formatting in the patch.
                nr = ny
                nth = nx
                data = np.zeros((nr, nth))
                # Read the data file.
                for i, line in enumerate(lines):
                    if not line.strip():
                        continue
                    values = line.split()
                    for j in range(nth):
                        data[i, j] = float(values[j].replace('D', 'E'))

                # Create a polar grid.
                max_radius = nr
                r = np.linspace(0, max_radius, nr)  # Radius range.
                theta = np.linspace(0, 2 * np.pi, nth)  # Angular range.
                R, Theta = np.meshgrid(r, theta, indexing='ij')

                # Convert to Cartesian coordinates.
                X = R * np.cos(Theta)
                Y = R * np.sin(Theta)

                # Map polar data to the Cartesian grid.
                x_cart = np.linspace(-max_radius, max_radius, 500)
                y_cart = np.linspace(-max_radius, max_radius, 500)
                X_cart, Y_cart = np.meshgrid(x_cart, y_cart)

                # Interpolate polar data onto the Cartesian grid.
                points = np.column_stack((X.ravel(), Y.ravel()))
                values = data.ravel()
                Z_cart = griddata(points, values, (X_cart, Y_cart), method='linear', fill_value=0)
                Z_cart_rot = np.rot90(Z_cart, k=-1)     # 0 degrees defaults to the 3 o'clock direction; rotate 90 degrees counterclockwise.

                if config.Grid_Ratio == 1:
                    extent = [-config.physical_R, config.physical_R, -config.physical_R, config.physical_R]
                else:
                    extent = [-max_radius, max_radius, -max_radius, max_radius]

                # Create a mask and set the area outside the circle to white.
                print("Creating the mask outside the device")
                mask = np.sqrt(X_cart ** 2 + Y_cart ** 2) > max_radius
                Z_cart_rot[mask] = np.nan       # Set the area outside the circle to NaN; it defaults to white.

                # Display the image.
                plt.imshow(Z_cart_rot, cmap='jet', origin='lower', extent=extent, aspect='equal')

                # Add a circular guide marker.
                circle_radius = max_radius if config.Grid_Ratio != 1 else config.physical_R
                circle = plt.Circle((0, 0), circle_radius, color='black', fill=False, linestyle='-', linewidth=1.5)
                plt.gca().add_artist(circle)  # Add the circle to the current axes.

                # Ensure the axis limits match the circle.
                plt.gca().set_xlim(-circle_radius, circle_radius)
                plt.gca().set_ylim(-circle_radius, circle_radius)

                # Colorbar.
                cb = plt.colorbar(label=config.colorbar_label, pad=0.05, shrink=0.8, extend='neither')
                cb.set_ticks(np.linspace(cb.vmin, cb.vmax, config.ticks_co))

                # Use scientific notation for the colorbar.
                formatter = ScalarFormatter(useMathText=True)
                formatter.set_powerlimits((0, 0))
                cb.formatter = formatter
                cb.update_ticks()

                # Force scientific notation (enable this if the code above does not work).
                #fmt = ticker.ScalarFormatter(useOffset=False, useMathText=False)
                #fmt.set_scientific(True)
                #fmt.set_powerlimits((0, 0))  # Use scientific notation for any nonzero exponent.
                #cb.formatter = fmt
                #cb.update_ticks()

                # Tick settings.
                ax = plt.gca()
                ax.xaxis.set_major_locator(LinearLocator(numticks=config.ticks_x))
                ax.yaxis.set_major_locator(LinearLocator(numticks=config.ticks_y))

                # Adjust major ticks: pad = label-to-axis distance, width = tick width,
                # length = tick-line length.
                ax.tick_params(axis='both', which='major', pad=8, width=1.2, length=8)

                disable_patch_4dp()  # Disable four-decimal formatting in the patch.
            else:
                print("Error cylindrical parameters")
            if config.show_title and config.title:
                plt.gca().set_title(config.title)
        plt.show(block=False)

