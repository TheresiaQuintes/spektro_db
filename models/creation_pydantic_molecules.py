from pydantic import BaseModel, ConfigDict, field_validator, computed_field
from typing import Type, Optional
import models.molecules as mol
import user.allowed_values as av


class MoleculeModel(BaseModel):
    molecular_formula: str
    structural_formula: str
    smiles: str
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

class SingleMoleculeModel(MoleculeModel):
    model_class: Type=mol.Single
    @field_validator("model_class")
    def check_grp(cls, v):
        if v is not mol.Single:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    name: str
    additional_info: Optional[str]=None


class RPModel(MoleculeModel):
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
