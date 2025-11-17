#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 12 10:50:30 2025

@author: quintes
"""
from sqlalchemy.orm import object_session
import read as r
import update as u


molecule = r.TDPFilter(id=1)
molecule = r.run_query(molecule)
molecule = molecule[0]



b = u.TDPUpdate()
b.linker = "co"
#b.doublet = "NO2"
#b.chromophore = "BDP1"
b.name = "abc"
u.update_model(molecule, b)


messung = r.TREPRFilter(id=1)
messung = r.run_query(messung)
messung = messung[0]

c = u.TREPRUpdate()
c.path = "//abc"

u.update_model(messung, c)
