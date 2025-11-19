from models.measurements import Measurement
from models.molecules import Molecule
from main import Session
import helpers.helper_functions as hf

session = Session()


def delete_object(obj):
    session.delete(obj)
    hf.safe_commit(session)

def delete_molecule(mol_id):
    obj = Molecule.query.filter(Molecule.id==mol_id).first()
    delete_object(obj)

def delete_measurement(mes_id):
    obj = Measurement.query.filter(Measurement.id==mes_id).first()
    delete_object(obj)
