from sqlalchemy.exc import SQLAlchemyError
from typing import Any, Optional, Type, Literal, Iterable
from pydantic import BaseModel, create_model, ConfigDict
from sqlalchemy.orm import DeclarativeMeta, class_mapper
from sqlalchemy.sql.sqltypes import String, Integer, Float, Boolean, Date, DateTime, Text
from sqlalchemy import inspect
from sqlalchemy.sql.sqltypes import Enum as SAEnum
import datetime



def safe_commit(session):
    try:
        session.commit()
    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Fehler beim Commit:", e)

def safe_flush(session):
    try:
        session.flush()
    except SQLAlchemyError as e:
        session.rollback()
        print("❌ Fehler beim Flush:", e)

from typing import get_origin, get_args, Union

def type_name_for_doc(typ):
    origin = get_origin(typ)
    # Optional[T] ist Union[T, NoneType]
    if origin is Union:
        args = [a for a in get_args(typ) if a is not type(None)]
        if args:
            t = args[0]
            return t.__name__ if hasattr(t, "__name__") else str(t)
    # normale Typen
    return typ.__name__ if hasattr(typ, "__name__") else str(typ)

def make_filter_model(model: Type[DeclarativeMeta]) -> Type[BaseModel]:
    """
    Erzeugt dynamisch eine Pydantic-Klasse für Filter basierend auf SQLAlchemy-Modellspalten.
    - Unterstützt Vererbung (auch Spalten aus Basisklassen)
    - Verhindert zusätzliche Felder (extra='forbid')
    """
    fields: dict[str, tuple[Any, None]] = {}

    # Verwende SQLAlchemy-Inspector, um ALLE Spalten (inkl. geerbte) zu bekommen
    mapper = inspect(model)
    for column in mapper.columns:
        field_name = column.name
        py_type = _map_sqla_type(column.type)

        # Basisfeld (Gleichheit)
        fields[field_name] = (Optional[py_type], None)

        # Vergleichsoperatoren für numerische oder zeitliche Typen
        if py_type in (int, float) or py_type.__name__ in ("date", "datetime"):
            for op in ("gt", "lt", "ge", "le", "ne"):
                fields[f"{field_name}__{op}"] = (Optional[py_type], None)

        # String-Vergleiche
        if py_type == str:
            for op in ("like", "ilike", "contains"):
                fields[f"{field_name}__{op}"] = (Optional[str], None)

    # Dynamisch Pydantic-Modell erzeugen
    name = f"{model.__name__}Filter"

    FilterModel = create_model(
        name,
        __config__=ConfigDict(extra="forbid", validate_assignment=True),
        **fields,
    )

   # --- Docstring ---
    operator_lines = [
    " gt: greater than",
    " lt: less than",
    " ge: greater than or equal to",
    " le: less than or equal to",
    " ne: not equal",
    " like: SQL LIKE pattern match",
    " ilike: case-insensitive LIKE",
    " contains: substring match (for strings)",
    "",
    " Usage: append operator to the field name, e.g. 'temperature__gt=20'."
    ]
    operator_explanation = "; ".join(operator_lines)


    # Zeilenweise Felder + Typ
    field_lines = "\n".join(
        f"- {fname}: {type_name_for_doc(typ)}"
        for fname, (typ, _) in fields.items()
    )

    FilterModel.__doc__ = f"""
    Pydantic filter model for {model.__name__}.

    The following operators can (but do not have to) be applied to the
    attributes:

    {operator_explanation}

    The following fields can be selected:

    {field_lines}
    """
    FilterModel.__name__ = name
    FilterModel.__qualname__ = name
    FilterModel.model = model
    return FilterModel


def _map_sqla_type(sqlatype):
    """Hilfsfunktion, um SQLAlchemy-Typen auf Python-Typen zu mappen."""

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




def make_ordering_model(model: Type[DeclarativeMeta]) -> Type[BaseModel]:
    """
    Erzeugt dynamisch eine Pydantic-Klasse, um Sortierfelder (ASC/DESC)
    für ein SQLAlchemy-Modell zu definieren.
    """
    fields: dict[str, tuple[Any, None]] = {}

    # Alle Spalten inklusive Vererbung holen
    mapper = inspect(model)
    for column in mapper.columns:
        fields[column.key] = (Optional[Literal["asc", "desc"]], None)

    # Dynamisches Model erzeugen
    name = f"{model.__name__}Ordering"
    OrderingModel = create_model(
        name,
        **fields,
        __config__=ConfigDict(
    extra="forbid",
    validate_assignment=True
        ),
    )

    # Zeilenweise Felder + Typ
    field_lines = "\n".join(
        f"- {fname}: {type_name_for_doc(typ)}"
        for fname, (typ, _) in fields.items()
    )

    OrderingModel.__doc__ = f"""
    Pydantic ordering model for {model.__name__}.

    Choose "asc" (for ascending ordering) or "desc" (for descending ordering)
    for each attribute that shall be included in the ordering of the results.

    The following fields can be selected:

    {field_lines}
    """

    return OrderingModel



def make_update_model(
    model: Type[DeclarativeMeta],
    exclude_fields: Iterable[str] = (),
) -> Type[BaseModel]:

    if model.__module__ == "models.measurements":
        exclude_fields = ["id", "molecular_id", "method", "created_at", "updated_at"]
    elif model.__module__ == "models.molecules":
        exclude_fields = ["id", "group", "created_at", "updated_at"]
    else:
        raise ValueError("Unknown model class")

    fields: dict[str, tuple[Any, None]] = {}

    mapper = inspect(model)
    for column in mapper.columns:
        field_name = column.name

        if field_name in exclude_fields:
            continue

        py_type = _map_sqla_type(column.type)
        fields[field_name] = (Optional[py_type], None)  # alle Felder optional

    # Dynamisch Pydantic-Modell erzeugen
    name = f"{model.__name__}Update"

    UpdateModel = create_model(
        name,
        __config__=ConfigDict(extra="forbid", validate_assignment=True),
        **fields,
    )

    UpdateModel.__doc__ = f"Pydantic-Updatemodell für {model.__name__}"
    UpdateModel.model = model  # optional, um das SQLAlchemy-Modell zu referenzieren
    return UpdateModel
