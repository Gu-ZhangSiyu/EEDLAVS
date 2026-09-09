import os
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import LinearLocator
from io import StringIO
from PyQt5.QtWidgets import QApplication
mpl.use("Qt5Agg")      # Tell Matplotlib to use the active Qt5 backend.
from run_DebugError import ImagekaError, safe_open

def sub_single_array_line(config):
    try:
        try:
            data = []
            with safe_open(config.input_path, 'r') as file:
                lines = [l for l in file.readlines() if l.strip()]  # Skip blank lines.
            ny = len(lines)  # Number of rows.
            nx = len(lines[0].split())  # Number of columns.
            for line in lines:
                values = line.split()
                data.extend([float(v.replace('D', 'E')) for v in values])
            print(f"(columns, rows) = ({nx}, {ny})")
            array2D = np.array(data, dtype=float).reshape(ny, nx)
        except Exception as e:
            print(f"Error loading data: {e}")
            raise ImagekaError(f"Failed to load data: {e}")
        adjusted_line = config.choice_single_num - 1
        if config.choice_col_ro == 1:
            print("Extracting the selected row index")
            if adjusted_line < 0 or adjusted_line >= ny:
                print(f"Row index out of range (1, {ny})")
                raise ImagekaError("Failed to load data")
            selected_column = array2D[adjusted_line, :]
        else:
            print("Extracting the selected column index")
            if adjusted_line < 0 or adjusted_line >= nx:
                print(f"Column index out of range (1, {nx})")
                raise ImagekaError("Failed to load data")
            selected_column = array2D[:, adjusted_line]
        print(f"Selected line: = {config.choice_single_num}")

        max_value = np.max(selected_column)
        min_value = np.min(selected_column)
        plt.figure(figsize=(16, 6))
        ax = plt.gca()
        ax.xaxis.set_major_locator(LinearLocator(numticks=config.single_ticks_x)) # Show x-axis ticks.
        ax.yaxis.set_major_locator(LinearLocator(numticks=config.single_ticks_y)) # Show y-axis ticks.

        if config.single_range_x != 0:
            if config.center_range_x == 1:
                x_range_pg = np.linspace(-config.single_range_x / 2, config.single_range_x / 2, len(selected_column))
            else:
                x_range_pg = np.linspace(0, config.single_range_x, len(selected_column))
        else:
            length = nx if config.choice_col_ro == 1 else ny
            x_range_pg = np.arange(length)
        plt.plot(x_range_pg, selected_column, marker='o', linestyle='-', markersize=4)
        plt.grid(True)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0, 0), useMathText=True)

        # Generate ticks within the actual data range.
        xticks = np.linspace(x_range_pg[0], x_range_pg[-1], config.single_ticks_x)
        ax.set_xticks(xticks)

        # Add dashed reference lines.
        if config.single_cutoff_x:
            cutoff_x = config.single_cutoff_x
            plt.axvline(x=cutoff_x, color='r', linestyle='--', linewidth=3, label=config.single_cutoff_x_lable)
        if config.single_cutoff_y:
            cutoff_y = config.single_cutoff_y
            plt.axhline(y=cutoff_y, color='gray', linestyle='--', linewidth=3, label=config.single_cutoff_y_lable)
        if config.single_cutoff_x or config.single_cutoff_y:
            plt.legend()

        # Add the title.
        if config.single_title:
            ax.set_title(config.single_title)

        # Display the maximum and minimum values in the plot.
        if config.single_Extreme_value:
            #plt.text(0.95, 0.95, f'Max: {max_value:.16f}', transform=plt.gca().transAxes,
            #         fontsize=20, verticalalignment='top', horizontalalignment='right', color='red')
            #plt.text(0.95, 0.85, f'Min: {min_value:.16f}', transform=plt.gca().transAxes,
            #         fontsize=20, verticalalignment='top', horizontalalignment='right', color='blue')
            # Scientific notation.
            s_max, exp_max = f"{max_value:.3e}".split("e")
            s_min, exp_min = f"{min_value:.3e}".split("e")
            exp_max = int(exp_max)
            exp_min = int(exp_min)
            txt_max = f"Max: ${float(s_max):.3f}\\times10^{{{exp_max}}}$"
            txt_min = f"Min: ${float(s_min):.3f}\\times10^{{{exp_min}}}$"
            plt.text(0.95, 0.95, txt_max, transform=ax.transAxes, fontsize=20,
                verticalalignment='top', horizontalalignment='right', color='red')
            plt.text(0.95, 0.85, txt_min, transform=ax.transAxes, fontsize=20,
                verticalalignment='top', horizontalalignment='right', color='blue')
        plt.show(block=False)
    except Exception as e:
        print(f"Error drawing a single nz: {e}")
        raise ImagekaError(f"Failed to load data: {e}")

def sub_point_Selection(config):
    try:
        point_nr, point_nz = config.point_coords
        point_values = []
        file_list = sorted(os.listdir(config.file_path), key=lambda x: int(os.path.splitext(x)[0]))
        total_files = len(file_list)
        for idx, file_name in enumerate(file_list, 1):
            sys.stdout.write(f"Process {idx}/{total_files} : {file_name}\n")
            sys.stdout.flush()
            QApplication.processEvents()
            try:
                file_path = os.path.join(config.file_path, file_name)
                with safe_open(file_path, 'r') as file:
                    data_str = file.read().replace('D', 'E')
                data = np.loadtxt(StringIO(data_str))
                if config.cylindrical_point:
                    if data.size != config.NR * config.nth:
                        print(f"Data length does not match the 2D mode expectation: {file_path}")
                        raise ImagekaError("Failed to load data")
                    array2D = data.reshape(config.NR, config.nth)
                else:
                    if data.size != config.NR * config.nz:
                        print(f"Data length does not match the 2D mode expectation: {file_path}")
                        raise ImagekaError("Failed to load data")
                    array2D = data.reshape(config.NR, config.nz)
            except Exception as e:
                print(f"Error loading data: {e}")
                raise ImagekaError(f"Failed to load data: {e}")
            value = array2D[point_nr - 1, point_nz - 1]  # Get the value at the selected point.
            point_values.append(value)
        x_axis = range(1, len(point_values) + 1)
        plt.figure(figsize=(16, 6))
        plt.plot(x_axis, point_values, marker='o', linestyle='-', markersize=4)
        plt.title(f'Point Value at ({point_nr}, {point_nz}) across Files', pad=20)
        plt.grid(True)
        plt.show(block=False)
    except Exception as e:
        print(f"Error when plotting a line graph with specified points: {e}")
        raise ImagekaError(f"Failed to load data: {e}")
