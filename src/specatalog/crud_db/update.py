import specatalog.models.measurements as ms
import specatalog.models.molecules as mol
from specatalog.models.base import TimeStampedModel

import specatalog.helpers.helper_functions as hf
from typing import Union

from specatalog.main import Session
session = Session()

# %%
"""
Automatic creation of the update model using the
helper_functions module. The functions for the creation include an automatic
documentation for the classes. To add new classes add them to the
model_mapping-dictionariy.

"""

model_mapping_update = {
    "MeasurementUpdate": ms.Measurement,
    "TREPRUpdate": ms.TREPR,
    "CWEPRUpdate": ms.CWEPR,
    "PulseEPRUpdate": ms.PulseEPR,
    "MoleculeUpdate": mol.Molecule,
    "SingleMoleculeUpdate": mol.SingleMolecule,
    "RPUpdate": mol.RP,
    "TDPUpdate": mol.TDP,
    "TTPUpdate": mol.TTP,
}

updates = {}
for name, model in model_mapping_update.items():
    f = hf.make_update_model(model)
    f.__module__ = __name__
    f.__name__ = name
    updates[name] = f

globals().update(updates)
update_model_type = Union[tuple(updates.values())]


# %%
"""
***********************************************
***** Functions for updating the database *****
***********************************************

"""

def update_model(entry: TimeStampedModel, update_data: update_model_type):
    """
    Update a database entry using an update model.
    The entry is updated and commited. In case of multicomponent molecules
    the name is updated automatically using the components.

    Parameters
    ----------
    entry : TimeStampedModel
        Any object from the models.base.TimeStampedModel (=sqlalchemy model)
        class or from a subclass. The entry is updated.
    update_data : update_model_type
        Update model. The fields that are set determine which fields of the
        entry are updated. The type of the update_data model should fit the
        type of the entry. E.g. if the entry is an object of the class TREPR,
        the update_data should be an object of the class TREPRUpdate.

    Raises
    ------
    ValueError
        An error is raised if the update model contains attributes that are not
        part of the database entry.

    Returns
    -------
    None.

    """

    data = update_data.model_dump(exclude_none=True)

    for field, value in data.items():
        if hasattr(entry, field):
            setattr(entry, field, value)
        else:
            raise ValueError(f"{field} not valid.")


    automatic_name_update(entry, data)

    session.add(entry)
    hf.safe_commit(session)

    return



def automatic_name_update(entry: TimeStampedModel,
                          update_data: update_model_type):
    """
    Automatic update of the name of a multi-component molecule in a database
    entry.

    Parameters
    ----------
    entry : TimeStampedModel
        Any object from the models.base.TimeStampedModel (=sqlalchemy model)
        class or from a subclass. If the entry is an object of an multi-
        component molecule class (i.e. RP, TDP or TTP) the name attribute
        is automatically set using the single components of the molecule.
    update_data : update_model_type
        Update data. If components of the molecule name are changed this
        defines how the total name of the molecule is changed.

    Returns
    -------
    None

    """
    # map components of the molecules
    group_keys = {
        "rp": ["radical_1", "linker", "radical_2"],
        "tdp": ["chromophore", "linker", "doublet"],
        "ttp": ["triplet_1", "linker", "triplet_2"]
    }

    # check if a molecule name is changed by the update_data
    keys_to_check = [k for keys in group_keys.values() for k in keys]
    if not any(k in update_data for k in keys_to_check):
        return  # if not: do nothing


    # helper function: take component name from update_data if it is changed
    # in other cases: take it from the entry (entry is not changed)
    def get_value(field):
        val = update_data.get(field)
        if val is not None:
            return val.value
        else:
            return getattr(entry, field).value

    # build name
    entry.name = "-".join(get_value(k) for k in group_keys[entry.group])

    return
