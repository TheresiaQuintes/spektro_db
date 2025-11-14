#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 14 13:22:01 2025

@author: quintes
"""
import numpy as np
import re
from pathlib import Path

# ---------------------------------------------------------
# 1) DSC-Datei einlesen (Key-Value Paare)
# ---------------------------------------------------------
def read_dsc(dsc_path):
    params = {}
    with open(dsc_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or not line[0].isalpha():
                continue
            parts = line.split(None, 1)
            if len(parts) == 1:
                continue
            key, val = parts
            val = val.strip().strip("'")
            params[key] = val
    return params

# ---------------------------------------------------------
# 2) Datenformat bestimmen
# ---------------------------------------------------------
def dtype_from_irfmt(tag):
    tag = tag.upper()
    match tag:
        case "C": return np.int8
        case "S": return np.int16
        case "I": return np.int32
        case "F": return np.float32
        case "D": return np.float64
        case _:   raise ValueError(f"Unbekanntes IRFMT: {tag}")

# ---------------------------------------------------------
# 3) DTA-Datei laden
# ---------------------------------------------------------
def load_dta(dta_path, dims, dtype, endian):
    byte_order = "<" if endian == "LIT" else ">"
    full_dtype = np.dtype(byte_order + np.dtype(dtype).str[1:])
    data = np.fromfile(dta_path, dtype=full_dtype)
    return data.reshape(dims)

# ---------------------------------------------------------
# 4) Hauptfunktion (wie eprload_BrukerBES3T)
# ---------------------------------------------------------
def load_bes3t(base_path):
    base = Path(base_path)
    dsc = base.with_suffix(".DSC")
    dta = base.with_suffix(".DTA")

    params = read_dsc(dsc)

    # Dimensions
    nx = int(params["XPTS"])
    ny = int(params.get("YPTS", 1))
    nz = int(params.get("ZPTS", 1))

    if params.get("IKKF") == "CPLX":
        dims = (nx, 2, ny, nz)
    else:
        dims = (nx, ny, nz)

    # Data Format
    dtype = dtype_from_irfmt(params["IRFMT"])

    # Byte order
    endian = params.get("BSEQ", "BIG")

    # Abszisse (nur lineare Achsen, wie 99% der Fälle)
    xmin = float(params["XMIN"])
    xwid = float(params["XWID"])
    xaxis = np.linspace(xmin, xmin + xwid, nx)

    # Load DTA
    data = load_dta(dta, dims, dtype, endian)

    # Daten als 1D ausgeben (Standard-Fall)
    data = data.squeeze()

    return data, xaxis, params


data, x, params = load_bes3t("/home/quintes/Downloads/01_Q_2pBsw_TTM-Cz-9An_80K_dark")
