from pydantic import BaseModel, Field, ConfigDict, field_validator
from typing import Type, Optional
import models.measurements as ms
import user.allowed_values as av
import datetime

class MeasurementModel(BaseModel):
    molecular_id: int
    temperature: float = Field(..., gt=0)
    solvent: av.Solvents
    concentration: Optional[str]=None
    date: datetime.date
    measured_by : av.Names
    location: Optional[str]=None
    device: Optional[av.Devices]=None
    series: Optional[str]=None
    path: str
    corrected: bool
    evaluated: bool

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


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
