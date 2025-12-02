from sqlalchemy import inspect
from sqlalchemy.orm.session import Session
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy.sql.sqltypes as Sqltypes
from sqlalchemy.sql.sqltypes import String, Integer, Float, Boolean, Date, DateTime, Text
from sqlalchemy.sql.sqltypes import Enum as SAEnum
from pydantic import BaseModel, create_model, ConfigDict
from typing import Any, Optional, Literal, get_origin, get_args, Union
from specatalog.models.base import TimeStampedModel
import datetime
import textwrap

def safe_commit(session: Session) -> bool:
    """
    Commit database session. In case the commit is not successful return False
    and rollback the session.

    Parameters
    ----------
    session : Session
        A sqlalchemy-session. This session is to be commited.

    Returns
    -------
    success : bool
        True if the commit was successful. False if an SQLAlchemyError was
        raised during the commit.

    """
    try:
        session.commit()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error during commit: {e}")
        return False

def safe_flush(session: Session) -> bool:
    """
    Flush database session. In case the flush is not successful return False
    and rollback the session.

    Parameters
    ----------
    session : Session
        A sqlalchemy-session. This session is to be flushed.

    Returns
    -------
    success : bool
        True if the flush was successful. False if an SQLAlchemyError was
        raised during the flush.

    """
    try:
        session.flush()
        return True

    except SQLAlchemyError as e:
        session.rollback()
        print(f"Error during flush: {e}")
        return False



def _type_name_for_doc(typ: type) -> str:
    """
    Get the string of a type for automatic documentation. If typ is a
    Union[T, NoneType] (as it is the case for the type of optional arguments)
    T is returned.

    Parameters
    ----------
    typ : type
        Any type of an object or variable.

    Returns
    -------
    typ_string : str
        The string of the type.

    """
    origin = get_origin(typ)
    # union types
    if origin is Union:
        args = [a for a in get_args(typ) if a is not type(None)]
        if args:
            t = args[0]
            typ_string = t.__name__ if hasattr(t, "__name__") else str(t)
            return typ_string

    # normal types
    typ_string = typ.__name__ if hasattr(typ, "__name__") else str(typ)
    return typ_string



def _map_sqla_type(sqlatype: Sqltypes) -> type:
    """
    Map SQLAlchemy types to Python types.

    Parameters
    ----------
    sqlatype : Sqltypes
        An SQLAlchemy type.

    Returns
    -------
    type
        The Python type that corresponds the SQLAlchemy type.

    """
    if isinstance(sqlatype, SAEnum):
        return sqlatype.enum_class
    if isinstance(sqlatype, (Integer,)):
        return int
    elif isinstance(sqlatype, (Float,)):
        return float
    elif isinstance(sqlatype, (Boolean,)):
        return bool
    elif isinstance(sqlatype, (String, Text)):
        return str
    elif isinstance(sqlatype, (Date,)):
        return datetime.date
    elif isinstance(sqlatype, (DateTime,)):
        return datetime.datetime
    else:
        return Any


def make_filter_model(model: TimeStampedModel) -> BaseModel:
    """
    Create dynamically a pydantic-class for filtering based on an SQLAlchemy-
    model.

    Parameters
    ----------
    model : TimeStampedModel
        An SQLAlchemy model of the type TimeStampedModel or any subclass.

    Returns
    -------
    FilterModel : BaseModel
        The filter-model contains all column names as optional fields. The type
        of each field is determined by the type of the column. The default
        value is None. For numerical fileds additionally fields with comparison
        operators and for string-type fields text-comparison operators are
        created. When using the model no addtional fields are allowed.

    """
    mapper = inspect(model)  # get all columns of the SQLA-model

    # fill fields-dictionary
    fields: dict[str, tuple[Any, None]] = {}
    for column in mapper.columns:
        field_name = column.name
        py_type = _map_sqla_type(column.type)

        # add basisfield (equality) for all columns
        fields[field_name] = (Optional[py_type], None)

        # add comparison operators for numerical types
        if py_type in (int, float) or py_type.__name__ in ("date", "datetime"):
            for op in ("gt", "lt", "ge", "le", "ne"):
                fields[f"{field_name}__{op}"] = (Optional[py_type], None)

        # add comparison operators for strings
        if py_type == str:
            for op in ("like", "ilike", "contains"):
                fields[f"{field_name}__{op}"] = (Optional[str], None)

    # create pydantic model from fields-dictionary
    name = f"{model.__name__}Filter"

    FilterModel = create_model(
        name,
        __config__=ConfigDict(extra="forbid", validate_assignment=True),
        **fields,
    )

   # *** create docstring ***
    operator_lines = [
    " gt: greater than",
    " lt: less than",
    " ge: greater than or equal to",
    " le: less than or equal to",
    " ne: not equal",
    " like: SQL LIKE pattern match",
    " ilike: case-insensitive LIKE",
    " contains: substring match (for strings)",
    ]
    operator_explanation = "".join(
        f"\n\t\t- {op}"
        for op in operator_lines
    )


    field_lines = "".join(
        f"\n\t\t- {fname}: {_type_name_for_doc(typ)}"
        for fname, (typ, _) in fields.items()
    )  # field_name + type

    FilterModel.__doc__ = textwrap.dedent(
    f"""
    Pydantic filter model for {model.__name__}.

    The following operators can (but do not have to) be applied to the
    attributes by appending the operator to the field name, e.g.
    temperature__gt=20 (-> temperature > 20):

    {operator_explanation}

    The following fields can be selected:

    {field_lines}

    """
    )

    FilterModel.model = model  # add the original model to the FilterModel
    return FilterModel


def make_ordering_model(model: TimeStampedModel) -> BaseModel:
    """
    Create dynamically a pydantic-class for ordering based on an SQLAlchemy
    model.

    Parameters
    ----------
    model : TimeStampedModel
        An SQLAlchemy model of the type TimeStampedModel or any subclass.

    Returns
    -------
    OrderingModel : BaseModel
        The ordering-model contains all column names as optional fields with
        the default-value None. The value of the field can only be set to
        "asc" (to indicate ascending ordering) or "desc" (to indicate
        descending ordering). No additional fields can be created when using
        the model.

    """
    mapper = inspect(model)  # get all columns of the SQLA-model

    # fill fields-dictionary
    fields: dict[str, tuple[Any, None]] = {}
    for column in mapper.columns:
        fields[column.key] = (Optional[Literal["asc", "desc"]], None)

    # create pydantic model from fields-dictionary
    name = f"{model.__name__}Ordering"

    OrderingModel = create_model(
        name,
        **fields,
        __config__=ConfigDict(
    extra="forbid",
    validate_assignment=True
        ),
    )

    # *** create docstring ***
    field_lines = "".join(
        f"\n\t\t- {fname}: {_type_name_for_doc(typ)}"
        for fname, (typ, _) in fields.items()
    )

    OrderingModel.__doc__ = textwrap.dedent(
    f"""
    Pydantic ordering model for {model.__name__}.

    Choose "asc" (for ascending ordering) or "desc" (for descending ordering)
    for each attribute that shall be included in the ordering of the results.

    The following fields can be selected:

    {field_lines}

    """)

    return OrderingModel



def make_update_model(model: TimeStampedModel) -> BaseModel:
    """
    Create dynamically a pydantic-class for updating based on an SQLAlchemy
    model.

    Parameters
    ----------
    model : TimeStampedModel
        An SQLAlchemy model of the type TimeStampedModel. Has to be of the
        class Molecule or Measurement (or a subclass).

    Raises
    ------
    ValueError
        If the model is not of the class Molecule or Measurement an error is
        raised.

    Returns
    -------
    UpdateModel : BaseModel
        The update-model contains all column names as optional fields with
        the default-value None. The value of the field can be set to any
        value but must be the same type as the original column type. Fields
        that must not be updated are excluded from the UpdateModel.
        No additional fields can be created when using the model.

    """
    # define fields that must not be updated
    if model.__module__ == "specatalog.models.measurements":
        exclude_fields = ["id", "molecular_id", "method", "created_at", "updated_at"]
    elif model.__module__ == "specatalog.models.molecules":
        exclude_fields = ["id", "group", "created_at", "updated_at"]
    else:
        raise ValueError("Unknown model class")

    mapper = inspect(model)  # get all columns of the SQLA-model

    # fill fields-dictionary
    fields: dict[str, tuple[Any, None]] = {}
    for column in mapper.columns:
        field_name = column.name

        if field_name in exclude_fields:
            continue

        py_type = _map_sqla_type(column.type)
        fields[field_name] = (Optional[py_type], None)

    # create pydantic model from fields-dictionary
    name = f"{model.__name__}Update"

    UpdateModel = create_model(
        name,
        __config__=ConfigDict(extra="forbid", validate_assignment=True),
        **fields,
    )

   # *** create docstrin ***

    field_lines = "".join(
        f"\n\t\t- {fname}: {_type_name_for_doc(typ)}"
        for fname, (typ, _) in fields.items()
    )

    UpdateModel.__doc__ = textwrap.dedent(
    f"""
    Pydantic update model for {model.__name__}. The fields that are set
    are the parameters that shall be updateted in the database.

    The following fields can be selected:

    {field_lines}

    """)

    UpdateModel.model = model  # reference SQLA-model
    return UpdateModel
