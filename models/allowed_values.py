from enum import Enum as eEnum

class Solvents(str, eEnum):
    toluene = "toluene"
    water = "water"


class Devices(str, eEnum):
    leer = ""
    elexsys = "ELEXSYS"
    emx_nano = "EMXnano"


class FrequencyBands(str, eEnum):
    leer = ""
    s = "S"
    x = "X"
    q = "Q"
    w = "W"


class PulseExperiments(str, eEnum):
    peanut = "PEANUT"
    peldor = "PELDOR"
    tn = "TN"
    saturation_recovery = "SR"


class Chromophores(str, eEnum):
    bdp0 = "BDP0"
    bdp1 = "BDP1"
    ndi0 = "NDI0"
    pent = "PENT"
    per = "PER"
    pdi0 = "PDI0"
    pdi2 = "PDI2"
    pdi4 = "PDI4"
    por0 = "POR0"
    por1 = "POR1"
    por2 = "POR2"


class Doublets(str, eEnum):
    no1 = "NO1"
    no2 = "NO2"
    no3 = "NO3"
    no4 = "NO4"
    no5 = "NO5"
    tri = "TRI"


class Linker(str, eEnum):
    bi = "BI"
    co = "co"
    sup_h = "sup_H"
    xylene = "xy"


class Radicals(str, eEnum):
    trp = "TRP"
    flav = "FLAV"
