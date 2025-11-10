import models.measurements as ms
import models.molecules as mol
from main import session
from helper_functions import safe_commit
import datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
import models.allowed_values as av
from typing import Optional
from typing import Type

class MoleculeModel(BaseModel):
    molecular_formula: str
    structural_formula: str
    smiles: str
    model_config = ConfigDict(extra="forbid")

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


class MeasurementModel(BaseModel):
    molecular_id: int
    temperature: float = Field(..., gt=0)
    solvent: av.Solvents
    concentration: Optional[str]=None
    date: datetime.date
    location: Optional[str]=None
    device: Optional[av.Devices]=None
    series: Optional[str]=None
    path: str
    corrected: bool
    evaluated: bool

    model_config = ConfigDict(extra="forbid")


class CWEPRModel(MeasurementModel):
    measurement_class: Type=ms.CWEPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.CWEPR:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    frequency_band: av.FrequencyBands
    attenuation: float


class TREPRModel(MeasurementModel):
    measurement_class: Type=ms.TREPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.TREPR:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    frequency_band: av.FrequencyBands
    excitation_wl: float
    excitation_energy: Optional[float]=None
    attenuation: float
    number_of_scans: Optional[int]=None
    repetitionrate: Optional[float]=None
    mode: Optional[str]=None


class PulseEPRModel(MeasurementModel):
    measurement_class: Type=ms.PulseEPR
    @field_validator("measurement_class")
    def check_grp(cls, v):
        if v is not ms.PulseEPR:
            raise ValueError("model_class darf nicht geändert werden")
        return v

    frequency_band: Optional[av.FrequencyBands]=None
    dsc_path: str
    pulse_experiment: av.PulseExperiments


def create_new_measurement(data):
    molecule = mol.Molecule.query.filter(
        mol.Molecule.id == data.molecular_id).first()
    print(type(molecule))
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
