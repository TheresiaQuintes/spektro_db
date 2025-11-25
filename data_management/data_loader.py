"""Code taken from the epyrtools project by BertainaS
 (https://github.com/BertainaS/epyrtools)"""


import numpy as np
from pathlib import Path
import warnings
import re

from typing import List, Union


# Regular expression to check if a string can be converted to a number
_NUMBER_RE = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


def read_par_file(par_file_path: Path) -> dict:
    """Reads a Bruker ESP/WinEPR .par file (key-value pairs)."""
    parameters = {}
    if not par_file_path.is_file():
        raise FileNotFoundError(f"Cannot find the parameter file {par_file_path}")

    try:
        with open(par_file_path, "r", encoding="latin-1") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(maxsplit=1)
                if len(parts) < 1:
                    continue

                key = parts[0]
                # Check if key starts with a letter (basic validation)
                if not key[0].isalpha():
                    continue

                value = parts[1].strip() if len(parts) > 1 else ""

                # Remove surrounding single quotes if present
                if len(value) >= 2 and value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]

                # Basic cleaning of key for dictionary access if needed
                # Note: Bruker keys are typically valid identifiers
                # if not key.isidentifier():
                #    key = re.sub(r'\W|^(?=\d)', '_', key) # Simple sanitization

                parameters[key] = value
    except Exception as e:
        raise IOError(f"Error reading PAR file {par_file_path}: {e}") from e

    if parameters.get("JEX"):
        parameters["XAXIS_NAME"] = parameters["JEX"]
    if parameters.get("JUN"):
        parameters["XAXIS_UNIT"] = parameters["JUN"]
    if parameters.get("XXUN"):
        parameters["XAXIS_UNIT"] = parameters["XXUN"]
    if parameters.get("JEY"):
        parameters["YAXIS_NAME"] = parameters["JEY"]
    if parameters.get("XYUN"):
        parameters["YAXIS_UNIT"] = parameters["XYUN"]

    return parameters


def read_dsc_file(dsc_file_path: Path) -> dict:
    """Reads a Bruker BES3T .DSC file (key-value pairs, handles line continuation)."""
    parameters = {}
    if not dsc_file_path.is_file():
        raise FileNotFoundError(f"Cannot find the descriptor file {dsc_file_path}")

    lines = []
    try:
        with open(dsc_file_path, "r", encoding="latin-1") as f:
            lines = f.readlines()
    except Exception as e:
        raise IOError(f"Error reading DSC file {dsc_file_path}: {e}") from e

    processed_lines = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Handle line continuation characters '\'
        while line.endswith("\\"):
            i += 1
            if i < len(lines):
                line = line[:-1] + lines[i].strip()
            else:
                line = line[:-1]  # Remove trailing '\' even if it's the last line
        processed_lines.append(line.replace("\\n", "\n"))  # Replace escaped newlines
        i += 1

    for line in processed_lines:
        if not line:
            continue

        parts = line.split(maxsplit=1)
        if len(parts) < 1:
            continue

        key = parts[0]
        # Stop if Manipulation History Layer is reached
        if key.upper() == "#MHL":
            break
        # Skip lines not starting with a letter (comments, etc.)
        if not key[0].isalpha():
            continue

        value = parts[1].strip() if len(parts) > 1 else ""

        # Remove surrounding single quotes if present
        if len(value) >= 2 and value.startswith("'") and value.endswith("'"):
            value = value[1:-1]

        # Basic cleaning of key if needed (Bruker keys usually okay)
        # if not key.isidentifier():
        #     key = re.sub(r'\W|^(?=\d)', '_', key)

        parameters[key] = value
    if parameters.get("XNAM"):
        parameters["XAXIS_NAME"] = parameters["XNAM"]
        parameters["XAXIS_UNIT"] = parameters["XUNI"]
    if parameters.get("YNAM"):
        parameters["YAXIS_NAME"] = parameters["YNAM"]
        parameters["YAXIS_UNIT"] = parameters["YUNI"]

    return parameters


def parse_field_params(parameters: dict) -> dict:
    """
    Attempts to convert string values in a dictionary to numbers (int or float).
    """
    parsed_params = {}
    for key, value in parameters.items():
        if isinstance(value, str):
            # Try converting to int
            try:
                parsed_params[key] = int(value)
                continue
            except ValueError:
                pass
            # Try converting to float
            try:
                # Use regex for more robust float check if needed,
                # but direct conversion attempt is usually fine
                if _NUMBER_RE.match(value):
                    parsed_params[key] = float(value)
                else:
                    parsed_params[key] = value  # Keep as string if not number-like
            except ValueError:
                parsed_params[key] = value  # Keep original string if conversion fails
        else:
            parsed_params[key] = value  # Keep non-string values as they are
    return parsed_params


def get_matrix(
    data_file_path: Path,
    dimensions: List[int],
    number_format_code: str,
    byte_order: str,
    is_complex: Union[bool, np.ndarray],
) -> np.ndarray:
    """
    Reads binary data from a file into a NumPy array.

    Args:
        data_file_path: Path to the data file (.DTA, .spc).
        dimensions: List of dimensions [nx, ny, nz].
        number_format: String representing numpy dtype ('int8', 'int16', etc.).
        byte_order: 'ieee-be' (big) or 'ieee-le' (little).
        is_complex: Boolean indicating if the data is complex. Can be array for multi-channel.

    Returns:
        NumPy array with the data.
    """
    if not data_file_path.is_file():
        raise FileNotFoundError(f"Data file not found: {data_file_path}")

    # Determine numpy dtype and endianness
    dt_char = ">" if byte_order == "ieee-be" else "<"
    try:
        # Construct dtype using standard codes (e.g., '>f8', '<i4')
        dtype = np.dtype(f"{dt_char}{number_format_code}")
    except TypeError as e:  # Catch potential error during dtype creation
        # Add original exception context using 'from e'
        raise ValueError(f"Unsupported number format code: {number_format_code}") from e

    # Calculate expected number of elements
    n_points_total = int(np.prod(dimensions))
    if n_points_total == 0:
        return np.array([])

    # Handle potentially complex data reading
    # For now, assume is_complex is a single boolean
    # A more complex implementation could handle mixed real/complex channels
    is_complex_flag = (
        np.any(is_complex) if isinstance(is_complex, (list, np.ndarray)) else is_complex
    )

    if is_complex_flag:
        n_values_to_read = n_points_total * 2
        actual_dtype = dtype.base  # Read underlying real type
    else:
        n_values_to_read = n_points_total
        actual_dtype = dtype

    # Read raw data from file
    try:
        raw_data = np.fromfile(
            data_file_path, dtype=actual_dtype, count=n_values_to_read
        )
    except Exception as e:
        raise IOError(f"Error reading data file {data_file_path}: {e}") from e

    # Verify number of elements read
    if raw_data.size < n_values_to_read:
        raise IOError(
            f"Could not read expected number of data points from {data_file_path}. "
            f"Expected {n_values_to_read}, got {raw_data.size}."
        )
    elif raw_data.size > n_values_to_read:
        warnings.warn(
            f"Read more data points ({raw_data.size}) than expected ({n_values_to_read}) "
            f"from {data_file_path}. Truncating."
        )
        raw_data = raw_data[:n_values_to_read]

    # Combine real and imaginary parts if complex
    if is_complex_flag:
        if raw_data.size % 2 != 0:
            raise ValueError("Read odd number of values for complex data.")
        data = raw_data[::2] + 1j * raw_data[1::2]
    else:
        data = raw_data

    # Reshape the data - NumPy uses C order (last index fastest)
    # MATLAB uses Fortran order (first index fastest)
    # BES3T/ESP files are typically C-ordered (X varies fastest)
    # Reshape to (nz, ny, nx) if 3D, (ny, nx) if 2D, (nx,) if 1D
    shape_numpy_order = [
        d for d in dimensions[::-1] if d > 1
    ]  # Reverse and remove dims of size 1
    if not shape_numpy_order:  # If all dims are 1 or empty
        shape_numpy_order = (n_points_total,)

    try:
        # Use squeeze to remove dimensions of size 1, similar to MATLAB's behavior
        data = data.reshape(shape_numpy_order).squeeze()
        # If the result is 0-dim after squeeze (single point), make it 1-dim
        if data.ndim == 0:
            data = data.reshape(1)

    except ValueError as e:
        raise ValueError(
            f"Could not reshape data with {data.size} points into desired shape {shape_numpy_order}. Original dims: {dimensions}. Error: {e}"
        ) from e

    return data


def BrukerListFiles(path, recursive=False):
    """
    List all Bruker EPR data files (.DTA, .dta, .SPC, .spc) in the given directory.

    Args:
        path (str or Path): Path to the folder containing Bruker files.
        recursive (bool, optional): If True, search subfolders recursively. Defaults to False.

    Returns:
        list[Path]: Sorted list of Path objects for found files.
    """
    exts = {".dta", ".DTA", ".spc", ".SPC"}
    path = Path(path)
    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a valid directory.")

    if recursive:
        files = [p for p in path.rglob("*") if p.suffix in exts and p.is_file()]
    else:
        files = [p for p in path.iterdir() if p.suffix in exts and p.is_file()]

    return sorted(files)



def load(full_base_name: Path, file_extension: str, scaling: str) -> tuple:
    """
    Loads Bruker BES3T data (.DTA, .DSC).

    Args:
        full_base_name: Path object without extension.
        file_extension: The original file extension (e.g., '.dta', '.dsc').
        scaling: Scaling string (e.g., 'nP G').

    Returns:
        tuple: (data, abscissa, parameters)
    """
    # Determine DSC and DTA file extensions, respecting case
    dsc_extension = ".dsc"
    dta_extension = ".dta"
    if file_extension.isupper():
        dsc_extension = dsc_extension.upper()
        dta_extension = dta_extension.upper()

    dsc_file = full_base_name.with_suffix(dsc_extension)
    dta_file = full_base_name.with_suffix(dta_extension)

    # Read descriptor file
    parameters = read_dsc_file(dsc_file)

    # --- Determine complexity, dimensions, byte order, format ---
    is_complex = np.array([False])  # Default to real
    n_data_values = 1
    if "IKKF" in parameters:
        parts = parameters["IKKF"].split(",")
        n_data_values = len(parts)
        is_complex = np.array([p.strip().upper() == "CPLX" for p in parts])
    else:
        warnings.warn("IKKF not found in .DSC file. Assuming IKKF=REAL.")

    # Dimensions
    try:
        nx = int(parameters.get("XPTS", 0))
        ny = int(parameters.get("YPTS", 1))
        nz = int(parameters.get("ZPTS", 1))
    except (ValueError, TypeError) as e:
        raise ValueError(
            f"Could not parse dimensions (XPTS/YPTS/ZPTS) from DSC file: {e}"
        ) from e
    if nx == 0:
        raise ValueError("XPTS is missing or zero in DSC file.")
    dimensions = [nx, ny, nz]

    # Byte Order
    byte_order = "ieee-be"  # Default big-endian
    if "BSEQ" in parameters:
        bseq_val = parameters["BSEQ"].upper()
        if bseq_val == "BIG":
            byte_order = "ieee-be"
        elif bseq_val == "LIT":
            byte_order = "ieee-le"
        else:
            raise ValueError(f"Unknown BSEQ value '{parameters['BSEQ']}' in .DSC file.")
    else:
        warnings.warn("BSEQ not found in .DSC file. Assuming BSEQ=BIG (big-endian).")

    # Number Format (assuming same for real and imag if complex)
    number_format_code = None
    if "IRFMT" in parameters:
        # For simplicity, take the first format if multiple are listed
        irfmt_val = parameters["IRFMT"].split(",")[0].strip().upper()
        fmt_map = {
            "C": "i1",  # int8   -> i1
            "S": "i2",  # int16  -> i2
            "I": "i4",  # int32  -> i4
            "F": "f4",  # float32-> f4
            "D": "f8",
        }  # float64-> f8
        if irfmt_val in fmt_map:
            number_format = fmt_map[irfmt_val]
        elif irfmt_val in ("A", "0", "N"):
            raise ValueError(
                f"Unsupported or no data format IRFMT='{irfmt_val}' in DSC."
            )
        else:
            raise ValueError(f"Unknown IRFMT value '{irfmt_val}' in .DSC file.")
    else:
        raise ValueError("IRFMT keyword not found in .DSC file.")

    if "IIFMT" in parameters and np.any(is_complex):
        iifmt_val = parameters["IIFMT"].split(",")[0].strip().upper()
        if iifmt_val != parameters["IRFMT"].split(",")[0].strip().upper():
            warnings.warn(
                "IRFMT and IIFMT differ in DSC file. Using IRFMT for reading."
            )
            # Raise error? MATLAB code enforces identity. Let's warn for now.
            # raise ValueError("IRFMT and IIFMT in DSC file must be identical.")

    # --- Construct Abscissa ---
    abscissa_list = [None] * 3  # X, Y, Z
    axis_names = ["X", "Y", "Z"]
    axis_defined = [False] * 3

    for i, axis in enumerate(axis_names):
        dim_size = dimensions[i]
        if dim_size <= 1:
            continue

        axis_type = parameters.get(f"{axis}TYP", "IDX")  # Default to linear index

        if axis_type == "IGD":  # Indirect, non-linear axis
            companion_suffix = f".{axis}GF"
            if file_extension.isupper():
                companion_suffix = companion_suffix.upper()
            companion_file = full_base_name.with_suffix(companion_suffix)

            fmt_key = f"{axis}FMT"
            data_format_char = parameters.get(fmt_key, "D").upper()  # Default double
            fmt_map = {"D": "float64", "F": "float32", "I": "int32", "S": "int16"}
            if data_format_char not in fmt_map:
                warnings.warn(
                    f"Cannot read companion file format '{data_format_char}' for axis {axis}. Assuming linear."
                )
                axis_type = "IDX"  # Fallback to linear if format unknown
            else:
                companion_dtype_str = fmt_map[data_format_char]
                # Determine endianness for companion file (assume same as data)
                dt_char = ">" if byte_order == "ieee-be" else "<"
                companion_dtype = np.dtype(f"{companion_dtype_str}")#np.dtype(f"{dt_char}{companion_dtype_str}")

                if companion_file.is_file():
                    try:
                        axis_data = np.fromfile(
                            companion_file, dtype=companion_dtype, count=dim_size
                        )
                        if axis_data.size == dim_size:
                            abscissa_list[i] = axis_data
                            axis_defined[i] = True
                        else:
                            warnings.warn(
                                f"Could not read expected {dim_size} values from companion file {companion_file}. Assuming linear axis."
                            )
                            axis_type = "IDX"  # Fallback to linear
                    except Exception as e:
                        warnings.warn(
                            f"Error reading companion file {companion_file}: {e}. Assuming linear axis."
                        )
                        axis_type = "IDX"  # Fallback to linear
                else:
                    warnings.warn(
                        f"Companion file {companion_file} not found for non-linear axis {axis}. Assuming linear axis."
                    )
                    axis_type = "IDX"  # Fallback to linear

        if axis_type == "IDX":  # Linear axis
            min_key = f"{axis}MIN"
            wid_key = f"{axis}WID"
            try:
                minimum = float(parameters[min_key])
                width = float(parameters[wid_key])
                if dim_size > 1:
                    if width == 0:
                        warnings.warn(
                            f"{axis} range has zero width (WID=0). Using index range 0 to N-1."
                        )
                        # Use 0 to N-1 for indices if width is zero
                        abscissa_list[i] = np.arange(dim_size)
                    else:
                        # linspace is inclusive of endpoint
                        abscissa_list[i] = np.linspace(
                            minimum, minimum + width, dim_size
                        )
                elif dim_size == 1:
                    abscissa_list[i] = np.array([minimum])  # Single point axis
                else:  # dim_size == 0 ? Should not happen if XPTS>0
                    abscissa_list[i] = np.array([])

                axis_defined[i] = True
            except (KeyError, ValueError, TypeError):
                warnings.warn(
                    f"Could not read MIN/WID parameters for axis {axis}. Using default index."
                )
                abscissa_list[i] = np.arange(dim_size)  # Default to index
                axis_defined[i] = True  # Mark as defined (with index)

        elif axis_type == "NTUP":
            raise NotImplementedError("Cannot read data with NTUP axes.")

    # Consolidate abscissa
    defined_abscissae = [
        a for a, defined in zip(abscissa_list, axis_defined) if defined
    ]
    if len(defined_abscissae) == 1:
        abscissa = defined_abscissae[0]
    elif len(defined_abscissae) > 1:
        abscissa = defined_abscissae  # Return list for multiple dimensions
    else:
        abscissa = None  # No axes defined

    # --- Read Data Matrix ---
    # Assuming single data value type for now (n_data_values=1)
    # NOTE: Multiple data values per point (n_data_values > 1) not yet supported\n    # This would require handling interleaved data formats in some BES3T files
    if n_data_values > 1:
        warnings.warn(
            f"DSC file indicates {n_data_values} data values per point (IKKF). Only reading the first value."
        )
        # Adjust logic here if multiple channels need reading/combining

    data = get_matrix(dta_file, dimensions, number_format, byte_order, is_complex[0])

    # --- Scale Data ---
    if scaling and data is not None and data.size > 0:
        # Get experiment type and pre-scaling flag
        expt_type = parameters.get("EXPT", "CW").upper()
        is_cw = expt_type == "CW"
        # SctNorm indicates if Bruker software already applied some scaling
        data_prescaled = parameters.get("SctNorm", "false").lower() == "true"

        # Get parameters needed for scaling
        n_averages = None
        receiver_gain_db = None
        receiver_gain = None
        sampling_time_s = None
        sampling_time_ms = None
        mw_power_w = None
        mw_power_mw = None
        temperature_k = None

        try:
            n_averages = int(parameters.get("AVGS"))
        except (ValueError, TypeError, KeyError):
            pass
        try:
            receiver_gain_db = float(parameters.get("RCAG"))
        except (ValueError, TypeError, KeyError):
            pass
        try:
            sampling_time_s = float(parameters.get("SPTP"))  # Time in seconds
        except (ValueError, TypeError, KeyError):
            pass
        try:
            mw_power_w = float(parameters.get("MWPW"))  # Power in Watt
        except (ValueError, TypeError, KeyError):
            pass
        try:
            temperature_k = float(parameters.get("STMP"))  # Temperature in K
        except (ValueError, TypeError, KeyError):
            pass

        # Calculate derived values
        if receiver_gain_db is not None:
            receiver_gain = 10 ** (receiver_gain_db / 20.0)
        if sampling_time_s is not None:
            sampling_time_ms = sampling_time_s * 1000.0
        if mw_power_w is not None:
            mw_power_mw = mw_power_w * 1000.0

        # Apply scaling factors
        if "n" in scaling:
            if n_averages is not None and n_averages > 0:
                if data_prescaled:
                    # MATLAB errors here, let's warn
                    warnings.warn(
                        f"Cannot scale by number of scans ('n'): Data is already averaged (SctNorm=true, AVGS={n_averages})."
                    )
                else:
                    data = data / n_averages
            else:
                warnings.warn(
                    "Cannot scale by number of scans ('n'): AVGS missing, zero, or invalid."
                )

        if is_cw and "G" in scaling:
            if receiver_gain is not None and receiver_gain != 0:
                # Assume data not already scaled by gain, even if SctNorm=true
                # (Bruker scaling details can be complex)
                data = data / receiver_gain
            else:
                warnings.warn(
                    "Cannot scale by receiver gain ('G'): RCAG missing or invalid."
                )

        if is_cw and "c" in scaling:
            if sampling_time_ms is not None and sampling_time_ms > 0:
                # MATLAB notes Xepr scales even if SctNorm=false. Assume we should always scale if requested.
                # if data_prescaled:
                #    warnings.warn("Scaling by conversion time ('c') requested, but data may already be scaled (SctNorm=true). Applying anyway.")
                data = data / sampling_time_ms
            else:
                warnings.warn(
                    "Cannot scale by conversion time ('c'): SPTP missing, zero, or invalid."
                )

        if is_cw and "P" in scaling:
            if mw_power_mw is not None and mw_power_mw > 0:
                data = data / np.sqrt(mw_power_mw)
            else:
                warnings.warn(
                    "Cannot scale by microwave power ('P'): MWPW missing, zero, or invalid."
                )
        elif not is_cw and "P" in scaling:
            warnings.warn(
                "Microwave power scaling ('P') requested, but experiment is not CW."
            )

        if "T" in scaling:
            if (
                temperature_k is not None
            ):  # Allow T=0K ? MATLAB doesn't error but scaling makes no sense. Let's scale anyway.
                if temperature_k == 0:
                    warnings.warn(
                        "Temperature (STMP) is zero. Scaling by T will result in zero."
                    )
                data = data * temperature_k
            else:
                warnings.warn(
                    "Cannot scale by temperature ('T'): STMP missing or invalid."
                )

    # Parse string parameters to numbers where possible
    parameters = parse_field_params(parameters)

    return data, abscissa, parameters
