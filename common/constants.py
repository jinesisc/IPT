
"""Physical constants (SI units). Import from here so every problem uses the same values."""

import numpy as np

G = 9.81                 # gravitational acceleration [m/s^2]
MU0 = 4e-7 * np.pi       # vacuum permeability [T*m/A]
K_B = 1.380649e-23       # Boltzmann constant [J/K]
RHO_AIR = 1.204          # air density at 20 C [kg/m^3]
ETA_AIR = 1.81e-5        # air dynamic viscosity at 20 C [Pa*s]
RHO_WATER = 998.0        # water density at 20 C [kg/m^3]
