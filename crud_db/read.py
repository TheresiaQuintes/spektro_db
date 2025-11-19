import helpers.helper_functions as hf
import models.measurements as ms
import models.molecules as mol
from main import Session

session = Session()

# Filter models
MeasurementFilter = hf.make_filter_model(ms.Measurement)
TREPRFilter = hf.make_filter_model(ms.TREPR)
CWEPRFilter = hf.make_filter_model(ms.CWEPR)
PulseEPRFilter = hf.make_filter_model(ms.PulseEPR)

MoleculeFilter = hf.make_filter_model(mol.Molecule)
SingleMoleculeFilter = hf.make_filter_model(mol.Single)
RPFilter = hf.make_filter_model(mol.RP)
TDPFilter = hf.make_filter_model(mol.TDP)
TTPFilter = hf.make_filter_model(mol.TTP)


# Ordering models
MeasurementOrdering = hf.make_ordering_model(ms.Measurement)
TREPROrdering = hf.make_ordering_model(ms.TREPR)
CWEPROrdering = hf.make_ordering_model(ms.CWEPR)
PulseEPROrdering = hf.make_ordering_model(ms.PulseEPR)

MoleculeOrdering = hf.make_ordering_model(mol.Molecule)
SingleMoleculeOrdering = hf.make_ordering_model(mol.Single)
RPOrdering = hf.make_ordering_model(mol.RP)
TDPOrdering = hf.make_ordering_model(mol.TDP)
TTPOrdering = hf.make_ordering_model(mol.TTP)


def run_query(filters, ordering=None):
    model = filters.model

    query = session.query(model)

    # Filter verarbeiten
    filter_dict = filters.model_dump(exclude_none=True, exclude={"model"})
    for key, value in filter_dict.items():
        if "__" in key:
            field_name, op = key.split("__", 1)
        else:
            field_name, op = key, "eq"

        if not hasattr(model, field_name):
            raise ValueError(f"Ungültiges Feld '{field_name}' für {model.__tablename__}")

        column = getattr(model, field_name)

        if op == "eq":
            query = query.filter(column == value)
        elif op == "ne":
            query = query.filter(column != value)
        elif op == "gt":
            query = query.filter(column > value)
        elif op == "ge":
            query = query.filter(column >= value)
        elif op == "lt":
            query = query.filter(column < value)
        elif op == "le":
            query = query.filter(column <= value)
        elif op == "like":
            query = query.filter(column.like(value))
        elif op == "ilike":
            query = query.filter(column.ilike(value))
        elif op == "contains":
            query = query.filter(column.contains(value))
        else:
            raise ValueError(f"Unbekannter Filteroperator: {op}")

    if ordering:
        for field, direction in ordering.model_dump(exclude_none=True).items():
            column = getattr(model, field, None)
            if column is None:
                raise ValueError(f"Ungültiges Feld: {field}")
            if direction == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())
    return query.all()
