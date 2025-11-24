import models.molecules as mol

from typing import TypeVar
from models.creation_pydantic_measurements import MeasurementModel
from models.measurements import Measurement
from models.creation_pydantic_molecules import MoleculeModel
from models.molecules import Molecule

from helpers.helper_functions import safe_commit, safe_flush
from main import Session, MOLECULES_PATH, MEASUREMENTS_PATH
session = Session()

measurement_model_pyd = TypeVar(
    "models.creation_pydantic_measurements.MeasurementModel",
    bound=MeasurementModel)
measurement_model_alc = TypeVar("models.measurements.Measurement",
                                bound=Measurement)
molecule_model_pyd = TypeVar(
    "models.creation_pydantic_molecules.MoleculeModel", bound=MoleculeModel)
molecule_model_alc = TypeVar("models.molecules.Measurement", bound=Molecule)

def create_new_measurement(data: measurement_model_pyd
                           ) -> measurement_model_alc:
    """
    Create a new database entry for the measurement table from a object of
    the class models.creation_pydantic_measurement.MeasurementModel

    The entry is created and the measurement_path is set automatically from the
    MEASUREMTS_PATH and the measurement-id.

    The entry is added and commited.

    Parameters
    ----------
    data : MeasurementModel
        Model from models.creation_pydantic_measurements. The subclass of the
        model classifies the experement e.g. cwEPR or trEPR.

    Raises
    ------
    ValueError
        A ValueError is raised in case the molecular id is not existent in the
        data base.

    Returns
    -------
    measurement : Measurement
        Object from the models.mesurements.Measurement class (=sqalchemy model)
        the subclass is dependent on the chosen method.

    """
    molecule = mol.Molecule.query.filter(
        mol.Molecule.id == data.molecular_id).first()
    if molecule is None:
        raise ValueError(f"No molecule with the ID \
                         MOL{data.molecular_id} found.")

    metadata = data.model_dump(exclude={"measurement_class"})
    measurement_class = data.measurement_class
    measurement = measurement_class(molecule=molecule, **metadata, path="")

    session.add(measurement)
    safe_flush(session)
    measurement.path = f"{MEASUREMENTS_PATH}/M{measurement.id}"

    safe_commit(session)

    return measurement



def create_new_molecule(data: molecule_model_pyd) -> molecule_model_alc:
    """
    Create a new database entry for the molecule table from a object of
    the class models.creation_pydantic_molecules.MoleculeModel.

    The entry is created and the path for the structural formula is set
    automatically from the MEASUREMTS_PATH and the molecule-id.

    The entry is added and commited.

    Parameters
    ----------
    data : MoleculeModel
        Model from models.creation_pydantic_molecules. The class of the
        model classifies the group of the molecule e.g. TDP or RP.

    Returns
    -------
    molecule : Molecule
        Object from the models.molecules.Molecule class (=sqalchemy model).
        The subclass is dependent on the chosen molecule group.

    """
    metadata = data.model_dump(exclude={"model_class"})
    model_class = data.model_class
    molecule = model_class(**metadata, structural_formula="")

    session.add(molecule)
    safe_flush(session)
    molecule.structural_formula = f"{MOLECULES_PATH}/MOL{molecule.id}"

    safe_commit(session)

    return molecule
