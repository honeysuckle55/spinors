"""General test script for GPE propagation on GPU."""
# pylint: disable=wrong-import-position
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

import numpy as np  # noqa: E402
# import torch  # noqa: E402
from matplotlib import pyplot as plt  # noqa: E402

from pspinor import pspinor as spin  # noqa: E402
from pspinor import tensor_tools as ttools  # noqa: E402


# BASIC STRUCTURE OF A SIMULATION:

# --------- 1. SETUP --------------
# [ ] Instantiate some sort of spinor object
# [ ] Set directory information (optional; default is the package directory)
# [ ] Set up trap parameters (default values available)
# [ ] Set up interaction parameters (default values available)
# [ ] Set up Raman parameters
# [ ] Additional functions (e.g. seed vortices, shift momentum)
# [ ] Specify sampling, time step duration (needs a default)
# --------- 2. RUN ----------------
# [ ] Propagate (imaginary or real time; should be independent of spinor vs.
#     scalar)
# --------- 3. ANALYZE ------------
# [ ] Post analysis from final wavefunction (plots, vortex)
# [ ] Post analysis from sampled wavefunctions (e.g. energy exp., populations,
#                                               max density)
# --------- 4. REPEAT -------------

# -------------------------------------------------------------------
# Test Case #1: Simple imaginary time propagation to the ground state

# --------- 1. SETUP --------------

# All of the wavefunctions and simulation parameters (e.g. psi, psik,
# TF parameters, trap frequencies, Raman parameters, directory paths) will
# be contained in a PSpinors object, with class methods for propagation
# (real & imaginary).

DATA_PATH = 'ground_state/Trial_000'
# The directory might look like:
#     spinor_gpe
#     ├── pspinors
#     |    ├── __init__.py
#     |    ├── pspinor.py
#     |    ├── tensor_tools.py
#     |    ├── tensor_propagator.py
#     |    └── prop_result.py
#     ├── constants.py
#     ├── data
#     |    ├── {project_name1}
#     |    |    ├── {Trial_000}
#     |    |    |   ├── code
#     |    |    |   |   └── this_script.py
#     |    |    |   ├── trial_data
#     |    |    |   |   ├── sampled_wavefunctions.npy
#     |    |    |   |   └── initial_wavefunction.npy
#     |    |    |   ├── description.txt
#     |    |    |   ├── assorted_images.png
#     |    |    |   └── assorted_videos.mp4
#     |    |    ├── {Trial_001}
#     |    |    |   └── ...
#     |    |    ├── {Trial_002}
#     |    |    |   └── ...
#     |    |    └── ...
#     |    ├── {project_name2}
#     |    |    ├── {Trial_000}
#     |    |    ├── {Trial_001}
#     |    |    ├── {Trial_002}
#     |    |    └── ...
#     |    ├── ...

FREQ = 50
W = 2*np.pi*FREQ
GAMMA = 1.0
ETA = 40.0

ATOM_NUM = 1e2
omeg = {'x': W, 'y': GAMMA*W, 'z': ETA*W}
g_sc = {'uu': 1.0, 'dd': 1.0, 'ud': 1.04}
pop_frac = (0.5, 0.5)
ps = spin.PSpinor(DATA_PATH, overwrite=True, atom_num=ATOM_NUM, omeg=omeg,
                  g_sc=g_sc, phase_factor=-1, is_coupling=False,
                  pop_frac=pop_frac, r_sizes=(8, 8), mesh_points=(128, 128))

plt.figure()
plt.imshow(ttools.density(ttools.fft_2d(ps.psi, ps.space['dr']))[0])
plt.show()

ps.coupling_setup(wavel=790.1)
ps.coupling_grad(2, 0)
ps.shift_momentum()

psi = ps.psi
psik = ttools.fft_2d(psi, ps.space['dr'])
psi_prime = ttools.ifft_2d(psik, ps.space['dr'])
print((np.abs(psi[0])**2 - np.abs(psi_prime[0])**2).max())

# --------- 2. RUN (Imaginary) ----
N_STEPS = 1000
dt = 1/50
is_sampling = True
device = 'cuda'

res0 = ps.imaginary(dt, N_STEPS, device, is_sampling=is_sampling)
# print(ps.prop.space)
# `res0` is an object containing the final wavefunctions, the energy exp.
# values, populations, average positions, and a directory path to sampled
# wavefunctions. It also has class methods for plotting and analysis.

# --------- 3. ANALYZE ------------
res0.plot_spins()
res0.plot_total()
res0.plot_eng()
res0.plot_pops()
res0.make_movie()

# --------- 4. SETUP --------------


# --------- 5. RUN (Real) ---------
N_STEPS = 2000
dt = 1/5000
is_sampling = True

res1 = ps.real(dt, N_STEPS, device, is_sampling=is_sampling)

# --------- 6. ANALYZE ------------
res1.plot_spins()
res1.plot_total()
res1.plot_eng()
res1.plot_pops()
res1.make_movie()
