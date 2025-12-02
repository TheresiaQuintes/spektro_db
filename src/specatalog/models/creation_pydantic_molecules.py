from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from typing import Type, Optional
import specatalog.models.molecules as mol

from specatalog.main import BASE_PATH
import importlib.util
spec = importlib.util.spec_from_file_location("allowed_values", BASE_PATH / "allowed_values.py")
av = importlib.util.module_from_spec(spec)
spec.loader.exec_module(av)


class MoleculeModel(BaseModel):
    """
    Pydantic model for creating new :class:`models.Molecule` entries.

    This model defines the minimal required input for creating a molecule in
    the database. It only includes essential molecular metadata; database-
    managed fields such as ``id`` or timestamps are excluded.

    Attributes
    ----------
    molecular_formula : str
        Standard chemical formula of the molecule (e.g., "C20H12").

    """
    molecular_formula: str
    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class SingleMoleculeModel(MoleculeModel):
    """
    Pydantic model for creating new :class:`mol.SingleMolecule` molecules.

    This subclass of :class:`MoleculeModel` adds fields specific to single-
    molecule entries. The ``model_class`` attribute is fixed to
    :class:`mol.SingleMolecule` and cannot be changed.

    Attributes
    ----------
    model_class : Type
        Always set to :class:`mol.SingleMolecule`. Attempting to assign a different
        class raises a validation error.
    name : str
        Human-readable name of the molecule. Must be unique.
    additional_info : str or None
        Optional free-text field with supplementary information.

    """
    model_class: Type=mol.SingleMolecule
    @field_validator("model_class")
    def check_grp(cls, v):
        if v is not mol.SingleMolecule:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    name: str
    additional_info: Optional[str]=None


class RPModel(MoleculeModel):
    """
    Pydantic model for creating new :class:`mol.RP` radical-pair molecules.

    This subclass of :class:`MoleculeModel` adds fields specific to
    radical-pair molecules. The ``model_class`` attribute is fixed to
    :class:`mol.RP` and cannot be changed. The ``name`` property is computed
    automatically from the radicals and linker.

    Attributes
    ----------
    model_class : Type
        Always set to :class:`mol.RP`. Attempting to assign a different class
        raises a validation error.
    radical_1 : av.Radicals
        Enumeration specifying the first radical centre.
    linker : av.Linker
        Enumeration specifying the chemical linker connecting the radicals.
    radical_2 : av.Radicals
        Enumeration specifying the second radical centre.
    name : str
        Computed property combining radicals and linker into a
        name (e.g., "TEMPO1-Ph-TEMPO2").
    """
    model_class: Type=mol.RP
    @field_validator("model_class")
    def check_grp(cls, v):
        if v is not mol.RP:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    radical_1: av.Radicals
    linker: av.Linker
    radical_2: av.Radicals

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.radical_1.value}-{self.linker.value}-{self.radical_2.value}"


class TDPModel(MoleculeModel):
    """
    Pydantic model for creating new :class:`mol.TDP` triplet–doublet–pair
    molecules.

    This subclass of :class:`MoleculeModel` adds fields specific to TDP
    molecules. The ``model_class`` attribute is fixed to :class:`mol.TDP`
    and cannot be changed.

    Attributes
    ----------
    model_class : Type
        Always set to :class:`mol.TDP`. Attempting to assign a different class
        raises a validation error.
    doublet : av.Doublets
        Enumeration specifying the doublet radical centre.
    linker : av.Linker
        Enumeration defining the chemical linker connecting the doublet and
        chromophore.
    chromophore : av.Chromophores
        Enumeration specifying the chromophoric unit in the TDP system.
    name : str
        Computed property combining doublet linker and chromophore into a
        name (e.g., "PDI2-co-TEMPO3").
    """
    model_class: Type=mol.TDP
    @field_validator("model_class")
    def check_grp(cls, v):
        if v is not mol.TDP:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    doublet: av.Doublets
    linker: av.Linker
    chromophore: av.Chromophores

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.chromophore.value}-{self.linker.value}-{self.doublet.value}"


class TTPModel(MoleculeModel):
    """
    Pydantic model for creating new :class:`mol.TTP` triplet–triplet–pair
    molecules.

    This subclass of :class:`MoleculeModel` adds fields specific to TTP
    molecules. The ``model_class`` attribute is fixed to :class:`mol.TTP` and
    cannot be changed. The ``name`` property is computed automatically from the
    triplets and linker.

    Attributes
    ----------
    model_class : Type
        Always set to :class:`mol.TTP`. Attempting to assign a different class
        raises a validation error.
    triplet_1 : av.Chromophores
        Enumeration specifying the first triplet-capable chromophore.
    linker : av.Linker
        Enumeration defining the chemical linker connecting the two triplets.
    triplet_2 : av.Chromophores
        Enumeration specifying the second triplet-capable chromophore.
    name : str
        Computed property combining triplet and linker values into a
        name (e.g., "Perylene-ph-Perylene").
    """
    model_class: Type=mol.TTP
    @field_validator("model_class")
    def check_grp(cls, v):
        if v is not mol.TTP:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    triplet_1: av.Chromophores
    linker: av.Linker
    triplet_2: av.Chromophores

    @computed_field
    @property
    def name(self) -> str:
        return f"{self.triplet_1.value}-{self.linker.value}-{self.triplet_2.value}"
