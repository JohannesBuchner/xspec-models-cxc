# xspec-models-cxc

Exploring ways to create a Python module that can let users use the
[XSPEC model
library](https://heasarc.gsfc.nasa.gov/xanadu/xspec/manual/XSappendixExternal.html)
with minimal effort. The idea would then be that packages like
[Sherpa](https://github/sherpa/sherpa) and
[3ML](https://github.com/threeML/threeML) could build on this package.

Well, that's the plan.

The home page for this module is
[xspec-models-cxc](https://github.com/cxcsds/xspec-models-cxc) and
have I mentioned that this is **very experimental**?

## LICENSE

This is released under the GNU GPL version 3 as this is built on code
developed for Sherpa and the CIAO contrib packages.

## How to build

You need to have XSPEC 12.12.0 installed, have the `HEADAS`
environment variable set up, and hope that your XSPEC build uses the
same versions of the libraries as mine does (since there's currently
no way to query XSPEC for these vaues programatically).

With this you can

```
% git clone https://github.com/cxcsds/xspec-models-cxc
% cd xspec-models-cxc
```

I suggest creating a new venv or conda environment, and then install
with the following (the `--log` option is useful when there are build
failures, which there will be!):

```
% pip install . --log=log
```

The build requires both
[pybind11](https://pybind11.readthedocs.io/en/stable/index.html) and
[parse-xspec](https://github.com/cxcsds/parse_xspec) but they will be
used automatically. Neither is required to use the compiled module.

I am not putting this on [PyPI](https://pypi.org/) yet as there are a
lot of things to work out first!

## Notes

There are 232 models in the heasoft-6.29 model.dat file, and this
module provides access to 231 of them (it's only the `pileup` model,
which is the one `acn` type) that is not supported.

| Type           | Total  | Supported |
| -------------- | ------ | --------- |
| additive       |    148 |       148 |
| multiplicative |     61 |        61 |
| convolution    |     22 |        22 |
| acn            |      1 |         0 |
| C++            |    135 |       134 |
| C              |      8 |         8 |
| FORTRAN        |     89 |        89 |

I had to

```
% export LD_LIBRARY_PATH=$HEADAS/lib
```

in order to use the module. I believe it depends on how you built the
XSPEC model library (I am using a full XSPEC installation).

## Quick run through

Here's a quick run through, which is available as
[scripts/example.py](https://raw.githubusercontent.com/cxcsds/xspec-models-cxc/main/scripts/example.py).
The Examples section below has more details.

```
import numpy as np

from matplotlib import pyplot as plt

import xspec_models_cxc as x

x.chatter(0)  # Hide the screen messages

print(f"Version: {x.get_version()}")

egrid = np.arange(0.1, 11, 0.01)
emid = (egrid[:-1] + egrid[1:]) / 2

for kT in [0.3, 0.5, 1, 3, 5, 10]:
    y = x.apec(energies=egrid, pars=[kT, 1, 0])
    plt.plot(emid, y, label=f'kT={kT}', alpha=0.6)

plt.xscale('log')
plt.yscale('log')

plt.legend()

plt.xlabel('Energy (keV)')
plt.ylabel('Photon/cm$^2$/s')
plt.title('APEC model: Abundance=1 Redshift=0')

plt.savefig('example-additive.png')

plt.clf()

for nH in [0.01, 0.05, 0.1, 0.5, 1]:
    y = x.phabs(energies=egrid, pars=[nH])
    plt.plot(emid, y, label=f'nH={nH}', alpha=0.6)

plt.xscale('log')
plt.yscale('log')

plt.legend()

plt.xlabel('Energy (keV)')
plt.ylabel('Relative')
plt.title('PHABS model')

plt.savefig('example-multiplicative.png')

plt.clf()

model = x.phabs(energies=egrid, pars=[0.05]) * x.apec(energies=egrid, pars=[0.5, 1, 0])
plt.plot(emid, model, label='Unconvolved', c='k', alpha=0.8)

for pars in [[0.1, 0], [0.2, -1], [0.2, 1]]:
    # the model argument gets over-written by gsmooth
    y = x.gsmooth(energies=egrid, pars=pars, model=model.copy())
    plt.plot(emid, y, label=f'$\sigma$={pars[0]} index={pars[1]}', alpha=0.8)

plt.xscale('log')
plt.yscale('log')

plt.legend()

plt.xlabel('Energy (keV)')
plt.ylabel('Photon/cm$^2$/s')
plt.title('GSMOOTH(PHABS * APEC)')

plt.savefig('example-convolution.png')

```

The screen output is just

```
Version: 12.12.0
```

and the plots are

### Additive model

![additive model](https://raw.githubusercontent.com/cxcsds/xspec-models-cxc/main/scripts/example-additive.png "additive model")

### Multiplicative model

![multipicative model](https://raw.githubusercontent.com/cxcsds/xspec-models-cxc/main/scripts/example-multiplicative.png "multiplicative model")

### Convolution model

![convolution model](https://raw.githubusercontent.com/cxcsds/xspec-models-cxc/main/scripts/example-convolution.png "convolution model")

## Examples

The XSPEC model library is automatically initalized when the first call
is made, not when the module is loaded. The `init` function provided
in version 0.0.5 and earlier is no-longer provided.

```
>>> import xspec_models_cxc as x
>>> x.__version__
'0.0.16'
>>> help(x)
Help on module xspec_models_cxc:

NAME
    xspec_models_cxc

DESCRIPTION
    Call XSPEC models from Python
    =============================

    Highly experimental.

    The XSPEC model library is automatically initialized on the first call
    to one of the functions or models.

    Support routines
    ----------------
    get_version - The version of the XSPEC model library.
    chatter - Get or set the XSPEC chatter level.
    abundance - Get or set the abundance-table setting.
    cross_section - Get or set the cross-section-table setting.
    elementAbundance - Return the abundance for an element by name or atomic number.
    elementName - Get the name of an element given the atomic number.
    cosmology - Get or set the cosmology (H0, q0, lambda0) settings.
    clearXFLT, getNumberXFLT, getXFLT, niXFLT, setXFLT - XFLT keyword handlnig.
    clearModelString, getModelString, setModelString - model string database.
    clearDb, getDb, setDb - keyword database.

    Additive models
    ---------------
    agauss - 2 parameters.
    agnsed - 15 parameters.
    agnslim - 14 parameters.
    apec - 3 parameters.
    bapec - 4 parameters.
...
    zpowerlw - 2 parameters.
    bwcycl - 12 parameters.

    Multiplicative models
    ---------------------
    absori - 6 parameters.
    acisabs - 8 parameters.
    constant - 1 parameters.
    cabs - 1 parameter.
...
    zwabs - 2 parameters.
    zwndabs - 3 parameters.

    Convolution models
    ------------------
    kyconv - 12 parameters.
    cflux - 3 parameters.
    clumin - 4 parameters.
    cpflux - 3 parameters.
    gsmooth - 2 parameters.
    ireflect - 7 parameters.
    kdblur - 4 parameters.
    kdblur2 - 6 parameters.
    kerrconv - 7 parameters.
    lsmooth - 2 parameters.
    partcov - 1 parameter.
    rdblur - 4 parameters.
    reflect - 5 parameters.
    rfxconv - 5 parameters.
    rgsxsrc - 1 parameter.
    simpl - 3 parameters.
    thcomp - 4 parameters.
    vashift - 1 parameter.
    vmshift - 1 parameters.
    xilconv - 6 parameters.
    zashift - 1 parameter.
    zmshift - 1 parameter.

FUNCTIONS
    SSS_ice(...) method of builtins.PyCapsule instance
        SSS_ice(*args, **kwargs)
        Overloaded function.

        1. SSS_ice(pars: numpy.ndarray[numpy.float32], energies: numpy.ndarray[numpy.float32], spectrum: int = 1) -> numpy.ndarray[numpy.float32]

        The XSPEC multiplicative SSS_ice model (1 parameter).

        2. SSS_ice(pars: numpy.ndarray[numpy.float32], energies: numpy.ndarray[numpy.float32], out: numpy.ndarray[numpy.float32], spectrum: int = 1) -> numpy.ndarray[numpy.float32]

        The XSPEC multiplicative SSS_ice model (1 parameter); inplace.

    TBabs(...) method of builtins.PyCapsule instance
        TBabs(*args, **kwargs)
        Overloaded function.

        1. TBabs(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

        The XSPEC multiplicative TBabs model (1 parameter).

        2. TBabs(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], out: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

        The XSPEC multiplicative TBabs model (1 parameter); inplace.

...

    zxipab(...) method of builtins.PyCapsule instance
        zxipab(*args, **kwargs)
        Overloaded function.

        1. zxipab(pars: numpy.ndarray[numpy.float32], energies: numpy.ndarray[numpy.float32], spectrum: int = 1) -> numpy.ndarray[numpy.float32]

        The XSPEC multiplicative zxipab model (5 parameters).

        2. zxipab(pars: numpy.ndarray[numpy.float32], energies: numpy.ndarray[numpy.float32], out: numpy.ndarray[numpy.float32], spectrum: int = 1) -> numpy.ndarray[numpy.float32]

        The XSPEC multiplicative zxipab model (5 parameters); inplace.

    zxipcf(...) method of builtins.PyCapsule instance
        zxipcf(*args, **kwargs)
        Overloaded function.

        1. zxipcf(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str
= '') -> numpy.ndarray[numpy.float64]

        The XSPEC multiplicative zxipcf model (4 parameters).

        2. zxipcf(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], out: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

        The XSPEC multiplicative zxipcf model (4 parameters); inplace.

DATA
    numberElements = 30

VERSION
    0.0.16

FILE
    /some/long/path/to//xspec-models-cxc/xspec_models_cxc.blah.blah

```

Note that you can see the difference between a FORTRAN model such as
`SSS_ice`, which deals with single-precision floats, and C/C++ models
such as `TBabs`, which deal with double-precision floats.

With this we can do a few things:

- what version of XSPEC are we using?

```
>>> help(x.get_version)
Help on built-in function get_version in module xspec_models_cxc:

get_version(...) method of builtins.PyCapsule instance
    get_version() -> str

    The version of the XSPEC model library

>>> x.get_version()
'12.12.0'
```

- playing with the chatter setting

```
>>> help(x.chatter)
Help on built-in function chatter in module xspec_models_cxc:

chatter(...) method of builtins.PyCapsule instance
    chatter(*args, **kwargs)
    Overloaded function.

    1. chatter() -> int

    Get the XSPEC chatter level.

    2. chatter(chatter: int) -> None

    Set the XSPEC chatter level.

>>> x.chatter()
10
>>> x.chatter(0)
>>> x.chatter()
0
>>> x.chatter(10)
```

- how about abundances tables?

```
>>> help(x.abundance)
Help on built-in function abundance in module xspec_models_cxc:

abundance(...) method of builtins.PyCapsule instance
    abundance(*args, **kwargs)
    Overloaded function.

    1. abundance() -> str

    Get the abundance-table setting.

    2. abundance(table: str) -> None

    Set the abundance-table setting.

>>> x.abundance()
'angr'
>>> x.abundance('lpgp')
 Solar Abundance Vector set to lpgp:  Lodders K., Palme H., Gail H.P., Landolt-Börnstein, New Series, vol VI/4B, pp 560–630 (2009) (Photospheric)
>>> x.abundance()
'lpgp'
>>> x.abundance('angr')
 Solar Abundance Vector set to angr:  Anders E. & Grevesse N. Geochimica et Cosmochimica Acta 53, 197 (1989)
```

It isn't clever enough to notice if you give it an unsupported
abundance name.

- what has atomic number 17?

```
>>> help(x.elementName)
Help on built-in function elementName in module xspec_models_cxc:

elementName(...) method of builtins.PyCapsule instance
    elementName(z: int) -> str

    Return the name of an element given the atomic number.

>>> x.elementName(17)
'Cl'
```

- what is the abundance of an element?

```
>>> help(x.elementAbundance)
Help on built-in function elementAbundance in module xspec_models_cxc:

elementAbundance(...) method of builtins.PyCapsule instance
    elementAbundance(*args, **kwargs)
    Overloaded function.

    1. elementAbundance(name: str) -> float

    Return the abundance setting for an element given the name.

    2. elementAbundance(z: int) -> float

    Return the abundance setting for an element given the atomic number.

>>> x.elementAbundance('Cl')
3.160000119351025e-07
>>> x.elementAbundance(17)
3.160000119351025e-07
```

Note that there's limited checking:

```
>>> >>> x.elementAbundance('Po')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
KeyError: 'Po'
>>> x.elementAbundance(256)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: 256
>>> x.elementAbundance(0)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
IndexError: 0
>>> x.elementAbundance(-4)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
TypeError: elementAbundance(): incompatible function arguments. The following argument types are supported:
    1. (name: str) -> float
    2. (z: int) -> float

Invoked with: -4
```

- can I evaluate a model?

### APEC (additive, C++)

The `model.dat` record for this model is

```
apec           3  0.         1.e20           C_apec    add  0
kT      keV     1.    0.008   0.008   64.0      64.0      .01
Abundanc " "    1.    0.      0.      5.        5.        -0.001
Redshift " "    0.   -0.999  -0.999   10.       10.       -0.01
```

So, if we want to use the default parameters - that is, kT=1,
Abundance=1, Redshift=0 - for the energy grid 0.1-0.2, 0.2-0.3,
0.3-0.4, and 0.4-0.5 we can say:

```
>>> import xspec_models_cxc as x
>>> help(x.apec)
Help on built-in function apec in module xspec_models_cxc:

apec(...) method of builtins.PyCapsule instance
    apec(*args, **kwargs)
    Overloaded function.

    1. apec(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '')
-> numpy.ndarray[numpy.float64]

    The XSPEC additive apec model (3 parameters).

    2. apec(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], out: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

    The XSPEC additive apec model (3 parameters); inplace.

>>> pars = [1, 1, 0]
>>> egrid = [0.1, 0.2, 0.3, 0.4, 0.5]
>>> x.apec(pars, egrid)
Reading APEC data from 3.0.9

array([2.10839183, 0.31196176, 0.22008776, 0.12295151])
>>>
```

We can see what dufference dropping the abundance to 0 makes:

```
>>> x.apec([1, 0, 0], egrid)
array([0.47038697, 0.21376409, 0.1247977 , 0.08182932])
```

Note that the return values have units of photons/cm^2/s as this is an
XSPEC [additive
model](https://heasarc.gsfc.nasa.gov/xanadu/xspec/manual/Additive.html).

### EVALUATING MODELS

Additive and multipicative models can either create a new output array
on each call - such as

```
>>> y = x.apec(pars=pars, energies=egrid)
```

or they can re-use an output array (in a similar manner to the `out`
argument of NumPy routines like
[np.cumsum](https://numpy.org/doc/stable/reference/generated/numpy.cumsum.html)):

```
>>> y = np.zeros(egrid.size - 1)
>>> yout = x.apec(pars=pars, energies=egrid, out=y)
>>> yout is y
True
```

### AGNSLIM (additive, FORTRAN)

The `agnslim` additive model is a FORTRAN model in 12.12.0:

```
agnslim         14 0.03       1.e20          agnslim  add  0
mass    solar  1e7     1.0     1.0     1.e10    1.e10     -.1
dist    Mpc    100    0.01    0.01    1.e9    1.e9     -.01
logmdot " "   1.    -10.      -10.       3 3     0.01
astar " " 0. 0. 0. 0.998 0.998 -1
cosi " "  0.5     0.05    0.05      1.   1.  -1
kTe_hot  keV(-pl)  100.0   10 10     300      300        -1
kTe_warm     keV(-sc)  0.2   0.1    0.1    0.5      0.5        1e-2
Gamma_hot    " "  2.4  1.3 1.3     3        3.       0.01
Gamma_warm      "(-disk)"  3.0  2    2     5.        10.       0.01
R_hot "Rg " 10.0 2.0 2.0 500 500 0.01
R_warm "Rg"   20.0  2 2 500 500     0.1
logrout "(-selfg) "   -1.0   -3.0    -3.0       7.0     7.0      -1e-2
rin   ""     -1      -1 -1 100. 100. -1
redshift   " "     0.0    0.      0.      5 5 -1
```

```
>>> help(x.agnslim)
Help on built-in function agnslim in module xspec_models_cxc:

agnslim(...) method of builtins.PyCapsule instance
    agnslim(*args, **kwargs)
    Overloaded function.

    1. agnslim(pars: numpy.ndarray[numpy.float32], energies: numpy.ndarray[numpy.float32], spectrum: int = 1) -> numpy.ndarray[numpy.float32]

    The XSPEC additive agnslim model (14 parameters).

    2. agnslim(pars: numpy.ndarray[numpy.float32], energies: numpy.ndarray[numpy.float32], out: numpy.ndarray[numpy.float32],
spectrum: int = 1) -> numpy.ndarray[numpy.float32]

    The XSPEC additive agnslim model (14 parameters); inplace.

>>> pars = [1e7, 100, 1, 0, 0.5, 100, 0.2, 2.4, 3, 10, 20, -1, -1, 0]
>>> egrid = np.arange(0.1, 11, 0.01)
>>> y = x.agnslim(pars, egrid)
>>> y
array([5.6430912e-01, 4.2761257e-01, 3.3259588e-01, ..., 2.6246285e-06,
       2.6130140e-06, 2.6132632e-06], dtype=float32)
```

### BWCYCL (additive, C)

This is a C-style additive model:

```
bwcycl     12  0.         1.e20           c_beckerwolff    add  0
Radius km      10        5      5       20      20      -1
Mass   Solar   1.4      1       1       3       3       -1
csi     " "     1.5      0.01    0.01    20         20        0.01
delta   " "     1.8      0.01    0.01    20         20        0.01
B       1e12G   4        0.01    0.01   100        100        0.01
Mdot    1e17g/s 1        1e-6   1e-6     1e6        1e6        0.01
Te      keV     5        0.1     0.1    100        100        0.01
r0      m       44        10    10     1000       1000        0.01
D       kpc     5          1     1       20         20        -1
BBnorm  " "     0          0     0       100       100        -1
CYCnorm " "     1          -1     -1       100       100        -1
FFnorm  " "     1          -1     -1       100       100        -1
```

```
>>> help(x.bwcycl)
Help on built-in function bwcycl in module xspec_models_cxc:

bwcycl(...) method of builtins.PyCapsule instance
    bwcycl(*args, **kwargs)
    Overloaded function.

    1. bwcycl(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

    The XSPEC additive bwcycl model (12 parameters).

    2. bwcycl(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], out: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

    The XSPEC additive bwcycl model (12 parameters); inplace.

>>> pars = [10, 1.3, 1.5, 1.8, 4, 1, 5, 44, 5, 0, 1, 1]
>>> x.bwcycl(pars, [0.5, 0.51, 0.52, 0.53, 0.54, 0.55, 0.56])
array([0.00030135, 0.00030085, 0.00030123, 0.00030297, 0.00030657,
       0.00031248])
```

### TBABS (multiplicative, C++)

The TBabs is a multiplicative model:

```
TBabs          1   0.03       1.e20          C_tbabs     mul 0
nH       10^22 1.  0.       0.      1E5       1E6       1E-3
```

With the default setting we don't expect much flux to get through for
the selected energy range (~0.1 - 0.5 keV), but this increases as nH
decreases by a magnitude or two:

```
>>> import numpy
>>> egrid = np.arange(0.1, 0.5, 0.05)
>>> x.abundance('wilm')
 Solar Abundance Vector set to wilm:  Wilms, J., Allen, A. & McCray, R. ApJ 542 914 (2000) (abundances are set to zero for those elements not included in the paper).
>>> help(x.TBabs)
Help on built-in function TBabs in module xspec_models_cxc:

TBabs(...) method of builtins.PyCapsule instance
    TBabs(*args, **kwargs)
    Overloaded function.

    1. TBabs(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

    The XSPEC multiplicative TBabs model (1 parameter).

    2. TBabs(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], out: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

    The XSPEC multiplicative TBabs model (1 parameter); inplace.

>>> x.TBabs([1], egrid)
tbvabs Version 2.3
Cosmic absorption with grains and H2, modified from
Wilms, Allen, & McCray, 2000, ApJ 542, 914-924
Questions: Joern Wilms
joern.wilms@sternwarte.uni-erlangen.de
joern.wilms@fau.de

http://pulsar.sternwarte.uni-erlangen.de/wilms/research/tbabs/

PLEASE NOTICE:
To get the model described by the above paper
you will also have to set the abundances:
   abund wilm

Note that this routine ignores the current cross section setting
as it always HAS to use the Verner cross sections as a baseline.
array([1.28407670e-175, 9.06810629e-062, 9.04157274e-029, 3.26034136e-016,
       2.02047907e-010, 5.09045226e-007, 3.97658583e-005])
>>> x.TBabs([0.1], egrid)
array([3.24234405e-18, 7.86595867e-07, 1.56900525e-03, 2.82700325e-02,
       1.07286588e-01, 2.34787860e-01, 3.63037122e-01])
>>> x.TBabs([0.01], egrid)
array([0.01782731, 0.24523089, 0.52427897, 0.70005576, 0.79993471,
       0.86510249, 0.90363929])
```

Note that the return values have no units as this is an XSPEC
[multiplicative
model](https://heasarc.gsfc.nasa.gov/xanadu/xspec/manual/Multiplicative.html).

### MKCFLOW (additive, C++)

The `mkcflow` additive model has a default of 0 for its redshift, but then
warns you about it!

```
mkcflow        5  0.         1.e20           C_xsmkcf    add  0
lowT    keV     0.1   0.0808  0.0808 79.9      79.9       0.001
highT   keV     4.    0.0808  0.0808 79.9      79.9       0.001
Abundanc " "    1.    0.      0.      5.        5.        0.01
Redshift " "    0.   -0.999  -0.999   10.       10.       -0.01
$switch    1     0       0     1      1       -1
```

```
>>> x.mkcflow([0.1, 4, 1, 0, 1], np.arange(0.1, 0.8, 0.1))

 XSVMCF: Require z > 0 for cooling flow models
array([0., 0., 0., 0., 0., 0.])
>>> x.mkcflow([0.1, 4, 1, 0, 1], np.arange(0.1, 0.8, 0.1))

 XSVMCF: Require z > 0 for cooling flow models
array([0., 0., 0., 0., 0., 0.])
```

unless you set the chatter to 0:

```
>>> x.chatter(0)
>>> x.mkcflow([0.1, 4, 1, 0, 1], np.arange(0.1, 0.8, 0.1))
array([0., 0., 0., 0., 0., 0.])
>>>
```

### SMAUG (additive, C)

The smaug model is an interesting one you have to set the XFLT keywords
before using it. The model is

```
smaug         22   0.0E+00    1.0E+20        c_xsmaug    add 0  1
kT.cc    keV       1.0E+00    8.0E-02 1.0E-01  1.0E+01  1.0E+02   1.0E-02
kT.dt    keV       1.0E+00    0.0E+00 0.0E+00  1.0E+01  1.0E+02   1.0E-02
kT.ix    " "       0.0E+00    0.0E+00 0.0E+00  1.0E+01  1.0E+01  -1.0E-03
kT.ir    Mpc       1.0E-01    1.0E-04 1.0E-04  1.0E+00  1.0E+00  -1.0E-03
kT.cx    " "       5.0E-01    0.0E+00 0.0E+00  1.0E+01  1.0E+01   1.0E-03
kT.cr    Mpc       1.0E-01    1.0E-04 1.0E-04  1.0E+01  2.0E+01   1.0E-02
kT.tx    " "       0.0E+00    0.0E+00 0.0E+00  1.0E+01  1.0E+01  -1.0E-03
kT.tr    Mpc       5.0E-01    1.0E-04 1.0E-04  1.0E+00  3.0E+00  -1.0E-02
nH.cc    cm**-3    1.0E+00    1.0E-06 1.0E-06  3.0E+00  3.0E+00  -1.0E-02
nH.ff    " "       1.0E-00    0.0E+00 0.0E+00  1.0E+00  1.0E+00  -1.0E-02
nH.cx    " "       5.0E-01    0.0E+00 0.0E+00  1.0E+01  1.0E+01   1.0E-03
nH.cr    Mpc       1.0E-01    1.0E-04 1.0E-04  1.0E+00  2.0E+00   1.0E-02
nH.gx    " "       0.0E+00    0.0E+00 0.0E+00  1.0E+01  1.0E+01  -1.0E-03
nH.gr    Mpc       2.0E-03    1.0E-04 1.0E-04  1.0E+01  2.0E+01  -1.0E-03
Ab.cc    solar     1.0E+00    0.0E+00 0.0E+00  3.0E+00  5.0E+00  -1.0E-02
Ab.xx    " "       0.0E+00    0.0E+00 0.0E+00  1.0E+01  1.0E+01  -1.0E-03
Ab.rr    Mpc       1.0E-01    1.0E-04 1.0E-04  1.0E+00  1.0E+00  -1.0E-02
redshift " "       1.0E-02    1.0E-04 1.0E-04  1.0E+01  1.0E+01  -1.0E+00
meshpts  " "       1.0E+01    1.0E+00 1.0E+00  1.0E+04  1.0E+04  -1.0E+00
rcutoff  Mpc       2.0E+00    1.0E+00 1.0E+00  3.0E+00  3.0E+00  -1.0E-02
mode     " "       1.0E+00    0.0E+00 0.0E+00  2.0E+00  2.0E+00  -1.0E+00
itype    " "       2.0E+00    1.0E+00 1.0E+00  4.0E+00  4.0E+00  -1.0E+00
```

and when you try to run it the model fails

```
>>> pars = [1, 1, 0, 0.1, 0.5, 0.1, 0, 0.5, 1, 0.1, 0.5, 0.1, 0, 2e-3, 1, 0, 0.1, 0.01, 10, 2, 1, 2]
>>> x.smaug(pars, [0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

***XSPEC Error:  in function XSmaug: cannot find XFLTnnnn keyword for inner annulus for spectrum 1

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: Caught an unknown exception!
```

We make probably make the error slightly nicer.

We can now set the XFLT keywords, but I'm making things up here so
it's not surprising it still fails:

```
>>> x.setXFLT(1, {'inner': 0, 'outer': 20, 'width': 0})
>>> x.setXFLT(2, {'inner': 20, 'outer': 40, 'width': 0})
>>> egrid = np.arange(0.1, 7, 0.01)
>>> y1 = x.smaug(pars, egrid, spectrum=2)

***XSPEC Error:  in function XSmaug: for of dataset 2 either the outer ring exceeds the cutoff radius, the outer ring is less
than or equal to the inner, or the sector width is zero

Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
RuntimeError: Caught an unknown exception!
```

(it also fails for `spectrum=1` in this case but I wanted to show that
the error message respected the spectrum value!)

### CFLUX convolution model (convolution, C++)

The `cflux` convolution model changes the normalization of the input
model so it matches 10^lg10Flux for the Emin to Emax range.

```
cflux        3  0.         1.e20             C_cflux   con 0
Emin    "keV"     0.5   0.0   0.0    1e6      1e6          -0.1
Emax    "keV"    10.0   0.0   0.0    1e6      1e6          -0.1
lg10Flux "cgs"  -12.0  -100.0 -100.0 100.     100.          0.01
```

Let's try to convolve a powerlaw over the range 0.5 to 10 keV:

```
>>> help(x.cflux)
Help on built-in function cflux in module xspec_models_cxc:

cflux(...) method of builtins.PyCapsule instance
    cflux(pars: numpy.ndarray[numpy.float64], energies: numpy.ndarray[numpy.float64], model: numpy.ndarray[numpy.float64], spectrum: int = 1, initStr: str = '') -> numpy.ndarray[numpy.float64]

    The XSPEC convolution cflux model (3 parameters); inplace.

>>> egrid = np.arange(0.4, 10.2, 0.1)
>>> pars = [0.5, 10, -12]
>>> y1 = x.powerlaw(pars=[-1.7], energies=egrid)
>>> y2 = x.cflux(pars=pars, energies=egrid, model=y1.copy())
```

Note that convolution models **always** over-write the `model`
argument - so if we had used `model=y1` rather than `model=y1.copy()`
then `y1` would have been changed (which is normally okay, but in this
example I wanted to compare the input and output arrays).

Now, we need to sum up `y2` over the range 0.5 to 10 keV,
which thanks to the grid I chose, is all-but the first and
last bins:

```
>>> egrid[:3], egrid[-3:]
(array([0.4, 0.5, 0.6]), array([ 9.9, 10. , 10.1]))
```

We shall use the mid-point of each bin for converting from
photons/cm^2/s to erg/cm^2/s, and as I can never remember the
conversion factor, let's calculate it

```
>>> emid_kev = (egrid[1:-2] + egrid[2:-1]) / 2
>>> import astropy.units as u
>>> ((1 * u.keV) / (1 * u.erg)).decompose()
<Quantity 1.60217663e-09>
>>> conv = ((1 * u.keV) / (1 * u.erg)).decompose().value
>>> emid_kev = (egrid[1:-2] + egrid[2:-1]) / 2
```

With this we can compare the flux of the model before and after
convolution by `cflux`. We can see the result is 1e-12 which matches
the lg10Flux parameter:

```
>>> (y1[1:-1] * emid_kev).sum() * conv
2.170144702398361e-06
>>> (y2[1:-1] * emid_kev).sum() * conv
9.999904093891366e-13
```
