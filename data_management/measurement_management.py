from pathlib import Path
import h5py
import shutil
from data_management.data_loader import load

""" If new SUPPORTED_FORMATS are added, ad them also to the functions
    new_raw_data_to_folder and new_raw_data_to_hdf5."""
SUPPORTED_FORMATS = {
    "bruker_bes3t": {".dsc", ".dta"},
}

CATEGORIES = ["raw", "scripts", "figures", "additional_info", "literature"]

def create_measurement_dir(base_dir, ms_id):
    path = Path(base_dir) / "data" / f"M{ms_id}"
    if path.exists():
        raise FileExistsError(f"Measurement folder {path} already exists!")


    for subdir in CATEGORIES:
        (path / subdir).mkdir(parents=True, exist_ok=True)

    measurement_path = (path / f"measurement_M{ms_id}.h5")
    if measurement_path.exists():
        raise FileExistsError(f"HDF5 file {measurement_path} already exists!")

    with h5py.File(measurement_path, "w") as f:
        f.create_group("raw_data")
        f.create_group("corrected_data")
        f.create_group("evaluations")
    return path

def measurement_path (base_dir, ms_id):
    ms_id = f"M{ms_id}"
    path = Path(base_dir) /"data"/ ms_id
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
        raw_data_3 = Path(raw_data).with_suffix(".YGF")
        if not raw_data_1.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_1}!")
        if not raw_data_2.exists():
            raise FileNotFoundError(f"Raw data not found at {raw_data_2}!")

        new_file_to_archive(raw_data_1, ms_id, "raw", base_dir, update=True)
        new_file_to_archive(raw_data_2, ms_id, "raw", base_dir, update=True)
        if raw_data_3.exists():
            new_file_to_archive(raw_data_3, ms_id, "raw", base_dir, update=True)

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
    hdf5_path = path / f"measurement_M{ms_id}.h5"
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

        data, x, params = load(dsc[0].with_suffix(""), "DSC", "n")

        new_dataset_to_hdf5(hdf5_path, data, "raw_data", "data")
        new_dataset_to_hdf5(hdf5_path, data.real, "raw_data", "data_real")
        new_dataset_to_hdf5(hdf5_path, data.imag, "raw_data", "data_imag")

        if type(x) == list:
            for n in range(len(x)):
                new_dataset_to_hdf5(hdf5_path, x[n], "raw_data", f"axis_{n}")
        else:
            new_dataset_to_hdf5(hdf5_path, x, "raw_data", "xaxis")

        with h5py.File(hdf5_path, "a") as f:
            grp = f.require_group("raw_data")
            for key, value in params.items():
                grp.attrs[key] = value

    return


def delete_element(base_dir, ms_id, category, filename, save_delete=True):
    if category not in CATEGORIES:
        raise ValueError(f"Ungültige Kategorie '{category}'. Erlaubt: {CATEGORIES}")

    path = measurement_path(base_dir, ms_id)
    file_path = path / category / filename

    if not file_path.exists():
        print(f"Datei existiert nicht: {file_path}")
        return False

    if save_delete:
        confirm = input(f"Datei wirklich löschen? {file_path} (y/N): ")
        if confirm.lower() != "y":
            print("Löschung abgebrochen.")
            return False

    file_path.unlink()
    print(f"Gelöscht: {file_path}")

    return

def delete_measurement(base_dir, ms_id, save_delete=True):
    path = measurement_path(base_dir, ms_id)
    if not path.exists():
        print(f"Messung existiert nicht: {path}")
        return

    if save_delete:
        confirm = input(f"GANZEN ORDNER löschen? {path} (y/N): ")
        if confirm.lower() != "y":
            print("Löschung abgebrochen.")
            return

    shutil.rmtree(path)
    print(f"Ordner gelöscht: {path}")
    return


def list_files(base_dir, ms_id, category=""):
    if category != "":
        if category not in CATEGORIES:
            raise ValueError(f"Ungültige Kategorie '{category}'. Erlaubt: {CATEGORIES}")

    path = measurement_path(base_dir, ms_id)
    folder = path / category

    if not folder.exists():
        return []   # Keine Fehler, einfach leere Liste zurückgeben


    files = list(folder.rglob("*"))

    # Nur echte Dateien/Ordner zurückgeben
    return [f for f in files if f.is_file()]
