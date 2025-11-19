import models.molecules as mol
from main import Session
from helpers.helper_functions import safe_commit

session = Session()


def create_new_measurement(data):
    molecule = mol.Molecule.query.filter(
        mol.Molecule.id == data.molecular_id).first()
    if molecule is None:
        raise ValueError(f"Kein Molekül mit ID {data.molecular_id} gefunden.")

    metadata = data.model_dump(exclude={"measurement_class"})
    measurement_class = data.measurement_class
    measurement = measurement_class(molecule=molecule, **metadata)

    session.add(measurement)
    safe_commit(session)


def create_new_molecule(data):
    metadata = data.model_dump(exclude={"model_class"})
    model_class = data.model_class
    molecule = model_class(**metadata)

    session.add(molecule)
    safe_commit(session)
