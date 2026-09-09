import os
import sys
import random
import time
import numpy as np
import matplotlib.pyplot as plt
from io import StringIO
from run_DebugError import ImagekaError, safe_open
from PyQt5.QtWidgets import QApplication

def analyze_single_file(file_path):
    with safe_open(file_path, 'r') as f:
        data_str = f.read().replace('D', 'E')
        data = np.loadtxt(StringIO(data_str))

    if data.ndim == 1:
        rows = 1
        cols = data.size
    else:
        rows, cols = data.shape
    total_elements = data.size
    print(f"data structure: ({rows}, {cols}) \nNumber of elements: {total_elements}")
    flat_data = data.flatten()      # Flatten the data into a one-dimensional array.
    variance = np.var(flat_data)
    std_dev = np.std(flat_data)
    print(f"Variance: {variance:.6f}")
    print(f"Standard deviation: {std_dev:.6f}")

    plt.figure(figsize=(20, 5))
    plt.plot(flat_data, marker='o', markersize=1, linestyle='-', color='b')
    plt.xlabel('indexing')
    plt.ylabel('value')
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    return variance, std_dev

def sub_file_extrema(filename):
    with safe_open(filename, 'r') as f:
        lines = f.readlines()
    data = [
        float(value.replace('D', 'E'))
        for line in lines if line.strip()
        for value in line.strip().split()
    ]
    if not data:
        print("File has no valid numeric data")
        sys.exit(1)

    minimum = min(data)
    maximum = max(data)
    print(f"Minimum: {minimum} \nMaximum: {maximum}")

def sub_path_extreme(pathname):
    # Get all files in the folder and group them by extension (case-sensitive).
    files_by_ext = {}
    for filename in os.listdir(pathname):
        file_path = os.path.join(pathname, filename)
        if os.path.isfile(file_path):
            _, ext = os.path.splitext(filename)
            if ext:
                ext = ext[1:]  # Remove the dot.
                if ext not in files_by_ext:
                    files_by_ext[ext] = []
                files_by_ext[ext].append(filename)

    # Iterate over each extension group.
    for ext, files in files_by_ext.items():
        if len(files) > 1:
            global_min = float('inf')   # Initialize the global minimum to positive infinity.
            global_max = float('-inf')  # Initialize the global maximum to negative infinity.
            total_files = len(files)

            for i, filename in enumerate(files, 1):
                file_path = os.path.join(pathname, filename)
                sys.stdout.write(f"\rProcessing '{ext}' {i}/{total_files} : {filename}")
                sys.stdout.flush()
                QApplication.processEvents()
                try:
                    with safe_open(file_path, 'r') as f:
                        lines = f.readlines()
                    data = [
                        float(value.replace('D', 'E'))
                        for line in lines if line.strip()
                        for value in line.strip().split()
                    ]
                    if not data:
                        print(f"\n!! File: '{filename}' has no valid numeric data")
                        continue
                    file_min = min(data)
                    file_max = max(data)

                    # Update the global minimum and maximum.
                    global_min = min(global_min, file_min)
                    global_max = max(global_max, file_max)

                except ValueError as e:
                    print(f"\n!! File: '{filename}' contains non-numeric data: {e}")
                except Exception as e:
                    print(f"\n!!Exception occurred in the processing of file '{filename}' : {e}")

            print("\n------------")
            # Check whether valid data was found.
            if global_min != float('inf') and global_max != float('-inf'):
                print(f"Global Maximum: {global_max}")
                print(f"Global Minimum: {global_min}")
            else:
                print(f"\n'{ext}' No valid numerical data in the file to calculate the extreme values")
        elif len(files) == 1:
            print(f"'{ext}' Only one file, please use the single file processing function: {files[0]}")


def _require_path(path, description, directory=False):
    if not path:
        raise ImagekaError(f"Please select {description} first")
    if directory:
        valid = os.path.isdir(path)
    else:
        valid = os.path.isfile(path)
    if not valid:
        raise ImagekaError(f"{description} does not exist or is unavailable: {path}")


def _load_numeric_data(file_path, dtype):
    """Load a numeric .bin file or a whitespace-delimited text data file."""
    if file_path.lower().endswith(".bin"):
        return np.fromfile(file_path, dtype=dtype)

    with safe_open(file_path, "r") as file_obj:
        data_str = file_obj.read().replace("D", "E").replace("d", "e")
    if not data_str.strip():
        return np.array([], dtype=dtype)
    return np.asarray(np.loadtxt(StringIO(data_str), dtype=dtype)).reshape(-1)


def extract_3d_to_2d(input_path, output_path, nx, ny, nz, xz_mode, plane, z_slice_index):
    """Extract an XZ or XY plane from a Fortran-ordered binary 3D field."""
    _require_path(input_path, "3D field input file")
    _require_path(output_path, "output directory", directory=True)
    if min(nx, ny, nz) <= 0:
        raise ImagekaError("3D field grid dimensions must be positive integers")
    if plane not in {"XZ", "XY"}:
        raise ImagekaError(f"Unknown slice plane: {plane}")
    if plane == "XZ" and xz_mode not in {0, 1}:
        raise ImagekaError("The XZ slice mode must be 0 or 1")
    if plane == "XY" and not 0 <= z_slice_index < nz:
        raise ImagekaError(f"Z-axis index {z_slice_index} is out of range; allowed range is 0 ~ {nz - 1}")

    print("\n" + "-" * 30)
    print("--- Starting 3D-to-2D plane extraction ---")
    try:
        data_1d = np.fromfile(input_path, dtype=np.float64)
        expected_size = nx * ny * nz
        if data_1d.size != expected_size:
            raise ImagekaError(f"Data size mismatch: expected {expected_size}, read {data_1d.size}")

        data_3d = data_1d.reshape((nx, ny, nz), order="F")
        mid_y = (ny - 1) // 2
        mid_x = (nx - 1) // 2
        if plane == "XZ":
            if xz_mode == 1:
                data_2d = data_3d[:, mid_y, :]
                mode_label = "full_xz"
            else:
                data_2d = data_3d[mid_x:, mid_y, :]
                mode_label = "half_rz"
        else:
            data_2d = data_3d[:, :, z_slice_index]
            mode_label = f"plane_xy_z{z_slice_index}"

        final_name = f"result_{mode_label}_{random.randint(0, 9999):04d}.txt"
        save_path = os.path.join(output_path, final_name)
        np.savetxt(save_path, data_2d, fmt="%.18e", delimiter=" ")
        print(f"Processing complete [mode {xz_mode}]: {mode_label}")
        print(f"Extracted 2D matrix shape: {data_2d.shape}")
        print(f"File saved to: {save_path}")
        print("-" * 30)
        return save_path
    except MemoryError as exc:
        raise ImagekaError("Out of memory; the grid is too large") from exc
    except ImagekaError:
        raise
    except Exception as exc:
        raise ImagekaError(f"Extraction failed: {exc}") from exc


def inspect_directory(folder_path, performance_duration=3.0):
    """Inspect directory size, file counts, empty files and binary read throughput."""
    _require_path(folder_path, "directory to inspect", directory=True)
    print("\n--- Starting directory-level data inspection ---")
    print(f"Target path: {folder_path}\nPlease wait...")

    total_size_bytes = 0
    total_files = 0
    bin_files_count = 0
    largest_bin_file = None
    largest_bin_size = -1
    smallest_bin_file = None
    smallest_bin_size = float("inf")
    zero_byte_files = []

    try:
        for root, _, files in os.walk(folder_path):
            for filename in files:
                total_files += 1
                file_path = os.path.join(root, filename)
                try:
                    file_size = os.path.getsize(file_path)
                except OSError:
                    continue
                total_size_bytes += file_size
                if file_size == 0:
                    zero_byte_files.append(filename)
                if filename.lower().endswith(".bin"):
                    bin_files_count += 1
                    if file_size > largest_bin_size:
                        largest_bin_size = file_size
                        largest_bin_file = file_path
                    if 0 < file_size < smallest_bin_size:
                        smallest_bin_size = file_size
                        smallest_bin_file = filename

        total_gb = total_size_bytes / (1024 ** 3)
        print(f"Total folder size: {total_gb:.4f} GB")
        print(f"Total files in folder: {total_files}")
        print(f"Number of .bin files: {bin_files_count}")
        if largest_bin_file:
            print(f"Largest .bin file: {os.path.basename(largest_bin_file)} ({_format_size(largest_bin_size)})")
        else:
            print("No valid .bin files found.")
        if smallest_bin_file and smallest_bin_size != float("inf"):
            print(f"Smallest non-empty .bin file: {smallest_bin_file} ({_format_size(smallest_bin_size)})")
        else:
            print("No non-empty .bin files found.")
        print(f"Number of 0 KB invalid/empty files: {len(zero_byte_files)}")
        if zero_byte_files:
            sample_zeros = ", ".join(zero_byte_files[:5])
            suffix = "..." if len(zero_byte_files) > 5 else ""
            print(f"   [Examples]: {sample_zeros}{suffix}")

        if largest_bin_file and largest_bin_size > 0:
            print("Estimating application-level sequential read performance...")
            chunk_size = 1024 * 1024 * 8
            start_time = time.perf_counter()
            bytes_read = 0
            with open(largest_bin_file, "rb") as file_obj:
                while time.perf_counter() - start_time < performance_duration:
                    data = file_obj.read(chunk_size)
                    if not data:
                        break
                    bytes_read += len(data)
            elapsed = time.perf_counter() - start_time
            if elapsed > 0:
                throughput_mb_s = (bytes_read / (1024 * 1024)) / elapsed
                print(f"Average application-level read speed: {throughput_mb_s:.2f} MB/s")
                print(f"Read {_format_size(bytes_read)} in {elapsed:.2f} seconds")
        else:
            print("Skipping read-throughput estimation because no valid sample is available.")
        print("Directory inspection complete")
    except Exception as exc:
        raise ImagekaError(f"Directory inspection failed: {exc}") from exc


def _format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_units = ("B", "KB", "MB", "GB", "TB")
    unit_index = min(int(np.floor(np.log(size_bytes) / np.log(1024))), len(size_units) - 1)
    unit_size = 1024 ** unit_index
    return f"{round(size_bytes / unit_size, 2)} {size_units[unit_index]}"


def check_invalid_values(file_path, precision="float64"):
    """Count NaN values in a binary field or text data file."""
    _require_path(file_path, "invalid-value check file")
    dtype = np.float64 if precision == "float64" else np.float32
    print("\n--- Starting invalid-value check ---")
    print(f"Parsing precision: {dtype.__name__}")
    try:
        data = _load_numeric_data(file_path, dtype)
        nan_count = int(np.isnan(data).sum())
        print(f"File: {os.path.basename(file_path)}")
        print(f"Total elements: {data.size}")
        print(f"NaN count: {nan_count}")
        print("Check complete" if nan_count == 0 else "Warning: invalid values found")
        return nan_count
    except Exception as exc:
        raise ImagekaError(f"Invalid-value check failed: {exc}") from exc


def compare_element_distributions(file1_path, file2_path, total_columns, x_column, precision="float64"):
    """Compare XYZ distributions for matching particle IDs in two .bin or text files."""
    _require_path(file1_path, "element comparison file 1")
    _require_path(file2_path, "element comparison file 2")
    if total_columns <= 0:
        raise ImagekaError("The total column count must be a positive integer")
    if not 1 <= x_column <= total_columns - 2:
        raise ImagekaError("The X-coordinate start column must leave X/Y/Z columns within the file range")

    dtype = np.float64 if precision == "float64" else np.float32
    print("\n--- Starting element distribution comparison ---")
    print(f"Parsing precision: {dtype.__name__}")
    try:
        data1_raw = _load_numeric_data(file1_path, dtype)
        data2_raw = _load_numeric_data(file2_path, dtype)
        if data1_raw.size % total_columns or data2_raw.size % total_columns:
            raise ImagekaError("The actual file size is not divisible by the configured total column count")
        data1 = data1_raw.reshape(-1, total_columns)
        data2 = data2_raw.reshape(-1, total_columns)
        x_index = x_column - 1
        print(f"Structure: {total_columns} columns, X is in column {x_column}")
        print(f"Particles in file 1: {len(data1)} | file 2: {len(data2)}")

        ids1 = data1[:, 0].astype(np.int64)
        ids2 = data2[:, 0].astype(np.int64)
        common_ids, indices1, indices2 = np.intersect1d(ids1, ids2, return_indices=True)
        if len(common_ids) == 0:
            print("Error: no matching particle IDs found")
            return None

        pos1 = data1[indices1, x_index:x_index + 3]
        pos2 = data2[indices2, x_index:x_index + 3]
        diff = pos1 - pos2
        distance_error = np.linalg.norm(diff, axis=1)
        norm1 = np.linalg.norm(pos1, axis=1)
        epsilon = 1e-16 if dtype == np.float64 else 1e-7
        relative_error = distance_error / np.where(norm1 < epsilon, epsilon, norm1) * 100.0
        max_abs_diff = np.max(np.abs(diff), axis=0)
        print(f"Common particles: {len(common_ids)}")
        print(f"Maximum relative error: {np.max(relative_error):.6f}%")
        print(f"Mean relative error: {np.mean(relative_error):.6f}%")
        print(f"Maximum absolute deviation by axis: X: {max_abs_diff[0]:.6f}, Y: {max_abs_diff[1]:.6f}, Z: {max_abs_diff[2]:.6f}")
        print("Comparison complete")
        return relative_error
    except ImagekaError:
        raise
    except Exception as exc:
        raise ImagekaError(f"Element distribution comparison failed: {exc}") from exc


def _compare_field_data(file1_path, file2_path, dimensions, dimension_label, precision):
    """Compare two numeric fields using the supplied 2D or 3D grid shape."""
    _require_path(file1_path, f"{dimension_label} field comparison file 1")
    _require_path(file2_path, f"{dimension_label} field comparison file 2")
    if any(dimension <= 0 for dimension in dimensions):
        raise ImagekaError(f"{dimension_label} field resolution must be a positive integer")

    dtype = np.float64 if precision == "float64" else np.float32
    expected_size = 1
    for dimension in dimensions:
        expected_size *= dimension
    print("\n" + "=" * 30)
    print(f"--- Starting {dimension_label} field distribution difference analysis ---")
    print(f"Parsing precision: {dtype.__name__}")
    try:
        data1 = _load_numeric_data(file1_path, dtype)
        data2 = _load_numeric_data(file2_path, dtype)
        if data1.size != expected_size or data2.size != expected_size:
            raise ImagekaError("The file data size does not match the configured resolution")

        print(f"Grid size: {' x '.join(str(dimension) for dimension in dimensions)}")
        print("Calculating field-difference norms...")
        diff = data1 - data2
        abs_diff = np.abs(diff)
        max_abs_error = np.max(abs_diff)
        mean_abs_error = np.mean(abs_diff)
        rmse = np.sqrt(np.mean(diff ** 2))
        max_value = np.max(np.abs(data1))
        if max_value == 0:
            if max_abs_error == 0:
                rel_l_inf = rel_l1 = rel_l2 = 0.0
            else:
                rel_l_inf = rel_l1 = rel_l2 = float("inf")
        else:
            rel_l_inf = max_abs_error / max_value * 100.0
            rel_l1 = mean_abs_error / max_value * 100.0
            rel_l2 = rmse / max_value * 100.0
        print(f"(Global reference maximum amplitude Max|F1|: {max_value:.6e})")
        print(f"L-infinity norm (maximum absolute error ratio): {rel_l_inf:.6f}%")
        print(f"L1 norm (mean absolute error ratio): {rel_l1:.6f}% (global)")
        print(f"L2 norm (root-mean-square error ratio RMSE): {rel_l2:.6f}% (local)")
        print("Comparison complete")
        print("=" * 30)
        return rel_l_inf, rel_l1, rel_l2
    except ImagekaError:
        raise
    except MemoryError as exc:
        raise ImagekaError("Out of memory") from exc
    except Exception as exc:
        raise ImagekaError(f"{dimension_label} field distribution comparison failed: {exc}") from exc


def compare_2d_fields(file1_path, file2_path, nx, ny, precision="float64"):
    """Compare two .bin or text 2D fields with L-infinity, L1 and L2 relative errors."""
    return _compare_field_data(file1_path, file2_path, (nx, ny), "2D", precision)


def compare_3d_fields(file1_path, file2_path, nx, ny, nz, precision="float64"):
    """Compare two .bin or text 3D fields with L-infinity, L1 and L2 relative errors."""
    return _compare_field_data(file1_path, file2_path, (nx, ny, nz), "3D", precision)


