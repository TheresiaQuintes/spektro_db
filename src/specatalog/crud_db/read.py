import specatalog.helpers.helper_functions as hf
import specatalog.models.measurements as ms
import specatalog.models.molecules as mol

from typing import Union

from specatalog.main import Session
session = Session()

#%%

"""
Automatic creation of the filter and ordering models using the
helper_functions module. The functions for the creation include an automatic
documentation for the classes. To add new classes add them to both of the
model_mapping-dictionaries.

"""

model_mapping_filters = {
    "MeasurementFilter": ms.Measurement,
    "TREPRFilter": ms.TREPR,
    "CWEPRFilter": ms.CWEPR,
    "PulseEPRFilter": ms.PulseEPR,
    "MoleculeFilter": mol.Molecule,
    "SingleMoleculeFilter": mol.SingleMolecule,
    "RPFilter": mol.RP,
    "TDPFilter": mol.TDP,
    "TTPFilter": mol.TTP,
}

filters = {}
for name, model in model_mapping_filters.items():
    f = hf.make_filter_model(model)
    f.__module__ = __name__
    filters[name] = f

globals().update(filters)
filter_model_type = Union[tuple(filters.values())]

model_mapping_ordering = {
    "MeasurementOrdering": ms.Measurement,
    "TREPROrdering": ms.TREPR,
    "CWEPROrdering": ms.CWEPR,
    "PulseEPROrdering": ms.PulseEPR,
    "MoleculeOrdering": mol.Molecule,
    "SingleMoleculeOrdering": mol.SingleMolecule,
    "RPOrdering": mol.RP,
    "TDPOrdering": mol.TDP,
    "TTPOrdering": mol.TTP,
}

ordering = {}
for name, model in model_mapping_ordering.items():
    f = hf.make_ordering_model(model)
    f.__module__ = __name__
    ordering[name] = f

globals().update(ordering)
ordering_model_type = Union[tuple(ordering.values())]



# %%
"""
****************************************
***** Function for running queries *****
****************************************

"""


def run_query(filters: filter_model_type, ordering: ordering_model_type=None
              ) -> list:
    """
    Query the database. The table is chosen from the filter model. All
    filters and the ordering is organised in filter and ordering models.

    Parameters
    ----------
    filters : filter_model
        Pydantic model from one of the Filter-classes. The class that is
        chosen determines which table is searched. If e.g. an object of the
        class TREPRFilter is used only trEPR-measurements are searched.
    ordering : ordering_model, optional
        The list of results may be ordered depending on one or muliple ordering
        parameters that are organised in an ordering model. For each parameter
        "asc" (ascending) or "desc" (descending) order can (but does not have
        to) be chosen. The default is None, which means that no ordering of the
        results is applied.

    Raises
    ------
    ValueError
        An error is raised if the filter or the ordering model contains
        attributes that are not part of the queried table.

    Returns
    -------
    list
        Results of the query. The lists contains objects of the sqlalchemy
        model type.

    """

    # get query instance
    model = filters.model
    query = session.query(model)

    # process filters
    filter_dict = filters.model_dump(exclude_none=True, exclude={"model"})
    for key, value in filter_dict.items():
        if "__" in key:
            field_name, op = key.split("__", 1)
        else:
            field_name, op = key, "eq"

        if not hasattr(model, field_name):
            raise ValueError(
                f"'{field_name}' not valid for {model.__tablename__}")

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
            raise ValueError(f"Unknown operator: {op}")

    # process ordering
    if ordering:
        for field_name, direction in ordering.model_dump(exclude_none=True).items():
            column = getattr(model, field_name, None)
            if column is None:
                raise ValueError(f"{field_name} not valid for {model.__tablename__}")
            if direction == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column.asc())

    # run query
    results = query.all()
    return results
