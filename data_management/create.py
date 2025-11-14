import json, os
from datetime import date
from pathlib import Path
import h5py
import shutil

def create_measurement_dir(base_dir, ms_id):
    ms_id = f"M{ms_id}"
    path = Path(base_dir) / ms_id
    if path.exists():
        raise FileExistsError(f"Measurement folder {path} already exists!")


    for subdir in ["raw", "scripts", "figures", "additional_info", "literature"]:
        (path / subdir).mkdir(parents=True, exist_ok=True)

    measurement_path = (path / "measurement.h5")
    if measurement_path.exists():
        raise FileExistsError(f"HDF5 file {measurement_path} already exists!")

    with h5py.File(measurement_path, "w") as f:
        f.create_group("raw_data")
        f.create_group("corrected_data")
        f.create_group("evaluations")
    return path


def new_raw_data(base_dir, ms_id, raw_data, data_type):
    ms_id = f"M{ms_id}"
    path = Path(base_dir) / ms_id
    if not path.exists():
        raise FileNotFoundError(f"Measurement folder {path} does not exist!")

    if data_type == "bes3t":
        raw_data_1 = Path(raw_data).with_suffix(".DSC")
        raw_data_2 = Path(raw_data).with_suffix(".DTA")
        if not raw_data_1.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_1}!")
        if not raw_data_2.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_2}!")

        ziel_1 = path / "raw" / raw_data_1.name
        ziel_2 = path / "raw" / raw_data_2.name

        if ziel_1.exists() or ziel_2.exists():
            raise FileExistsError(f"Measurement raw data at {ziel_1} already exists!")
        else:
            shutil.copy(raw_data_1, ziel_1)
            shutil.copy(raw_data_2, ziel_2)

            # Daten in hdf5 laden, Bild erstellen
    else:
        raise ValueError(f"Data type: {data_type} unknown!")
