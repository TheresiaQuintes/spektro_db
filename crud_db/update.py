import helpers.helper_functions as hf
import models.measurements as ms
import models.molecules as mol
from pydantic import BaseModel
from main import Session

session = Session()

# Update models
MeasurementUpdate = hf.make_update_model(ms.Measurement)
TREPRUpdate = hf.make_update_model(ms.TREPR)
CWEPRUpdate = hf.make_update_model(ms.CWEPR)
PulseEPRUpdate = hf.make_update_model(ms.PulseEPR)

MoleculeUpdate = hf.make_update_model(mol.Molecule)
SingleMoleculeUpdate = hf.make_update_model(mol.Single)
RPUpdate = hf.make_update_model(mol.RP)
TDPUpdate = hf.make_update_model(mol.TDP)
TTPUpdate = hf.make_update_model(mol.TTP)


def update_model(obj,  # SQLAlchemy-Instanz, z.B. TREPR
    update_data: BaseModel):
    """
    Aktualisiert ein SQLAlchemy-Objekt anhand eines Pydantic UpdateModels.
    """
    # Nur die Werte nehmen, die gesetzt sind
    data = update_data.model_dump(exclude_none=True)

    for field, value in data.items():
        if hasattr(obj, field):
            setattr(obj, field, value)
        else:
            raise ValueError(f"Ungültiges Feld: {field}")


    automatic_name_update(obj, data)

    session.add(obj)
    hf.safe_commit(session)



def automatic_name_update(obj, data):
    # Mapping: group → die Reihenfolge der Attribute für den Namen
    group_keys = {
        "rp": ["radical_1", "linker", "radical_2"],
        "tdp": ["chromophore", "linker", "doublet"],
        "ttp": ["triplet_1", "linker", "triplet_2"]
    }

    # Prüfen, ob mindestens einer der relevanten Keys vorhanden ist
    keys_to_check = [k for keys in group_keys.values() for k in keys]
    if not any(k in data for k in keys_to_check):
        return  # nichts zu tun


    # Helper: Wert aus data nehmen, sonst aus obj
    def get_value(field):
        val = data.get(field)
        if val is not None:
            return val.value
        else:
            return getattr(obj, field).value

    # Namen zusammensetzen
    obj.name = "-".join(get_value(k) for k in group_keys[obj.group])
