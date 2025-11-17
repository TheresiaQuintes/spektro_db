from pathlib import Path
import h5py
import shutil
from load_bruker_bes3t import load_bes3t

SUPPORTED_FORMATS = {
    "bruker_bes3t": {".dsc", ".dta"},
}

CATEGORIES = ["raw", "scripts", "figures", "additional_info", "literature"]

def create_measurement_dir(base_dir, ms_id):
    ms_id = f"M{ms_id}"
    path = Path(base_dir) / ms_id
    if path.exists():
        raise FileExistsError(f"Measurement folder {path} already exists!")


    for subdir in CATEGORIES:
        (path / subdir).mkdir(parents=True, exist_ok=True)

    measurement_path = (path / "measurement.h5")
    if measurement_path.exists():
        raise FileExistsError(f"HDF5 file {measurement_path} already exists!")

    with h5py.File(measurement_path, "w") as f:
        f.create_group("raw_data")
        f.create_group("corrected_data")
        f.create_group("evaluations")
    return path

def measurement_path (base_dir, ms_id):
    ms_id = f"M{ms_id}"
    path = Path(base_dir) / ms_id
    if not path.exists():
        raise FileNotFoundError(f"Measurement folder {path} does not exist!")
    return path


def new_file_to_archive(src, ms_id, category, base_dir, update=False):
    """
    Kopiert eine Datei in das Archiv unter:
    <archive_root>/<ms_id>/<category>/<dateiname>

    Parameters
    ----------
    src : str or Path
        Pfad zur Quelldatei.
    ms_id : str or int
        Nummer der Messung, z.B. "0034".
    category : str
        Eine der Kategorien: ["raw", "scripts", "figures", "additional_info", "literature"]
    archive_root : str or Path
        Basisordner des Archivs.
    """

    src = Path(src)
    path = measurement_path(base_dir, ms_id)

    # Kategorie prüfen
    if category not in CATEGORIES:
        raise ValueError(
            f"Ungültige Kategorie '{category}'. "
            f"Erlaubt sind: {', '.join(CATEGORIES)}."
        )

    if not src.exists():
        raise FileNotFoundError(f"Quelldatei existiert nicht: {src}")

    # Zielpfad konstruieren
    target_dir = path / category
    target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / src.name

    # Falls die Datei schon existiert → Version anhängen
    if target_file.exists():
        if not update:
            raise FileExistsError(f"File at {target_file} already exists! Use new name or update-function instead")

    # Datei kopieren (bzw. überschreiben)
    shutil.copy2(src, target_file)

    return

def new_dataset_to_hdf5(hdf5_path, data, group_name, set_name):
    with h5py.File(hdf5_path, "a") as f:
        group = f.require_group(group_name)
        group.create_dataset(set_name, data=data)
        f.close()
    return

def new_raw_data_to_folder(base_dir, ms_id, raw_data, fmt):
    if fmt == "bruker_bes3t":
        raw_data_1 = Path(raw_data).with_suffix(".DSC")
        raw_data_2 = Path(raw_data).with_suffix(".DTA")
        if not raw_data_1.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_1}!")
        if not raw_data_2.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_2}!")

        new_file_to_archive(raw_data_1, ms_id, "raw", base_dir, update=True)
        new_file_to_archive(raw_data_2, ms_id, "raw", base_dir, update=True)

    else:
        raise ValueError(f"Data type: {fmt} unknown!")


def detect_supported_format(folder: Path):
    suffixes = {f.suffix.lower() for f in folder.iterdir() if f.is_file()}

    for format_name, required_suffixes in SUPPORTED_FORMATS.items():
        # Wenn alle benötigten Endungen vorhanden sind
        if required_suffixes.issubset(suffixes):
            return format_name

    return None  # nichts bekanntes gefunden


def new_raw_data_to_hdf5(base_dir, ms_id):
    path = measurement_path(base_dir, ms_id)
    raw_path = path/"raw"
    fmt = detect_supported_format(raw_path)

    if fmt == None:
        raise ValueError("Fileformat not known.")

    elif fmt == "bruker_bes3t":
        dsc = [p for p in raw_path.iterdir() if p.suffix.lower() == ".dsc"]
        dta = [p for p in raw_path.iterdir() if p.suffix.lower() == ".dta"]

        if not dsc or not dta:
            raise ValueError("Es müssen genau eine DSC und eine DTA Datei vorhanden sein.")
        if dsc[0].stem != dta[0].stem:
            raise ValueError("DSC und DTA haben unterschiedliche Basenames!")

        data, x, params = load_bes3t(dsc[0].with_suffix(""))

        new_dataset_to_hdf5(path/"measurement.h5", data, "raw_data", "data")
        new_dataset_to_hdf5(path/"measurement.h5", x, "raw_data", "xaxis")

    return
