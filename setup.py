from setuptools import setup, Extension
from Cython.Build import cythonize

import numpy as np

extensions = [
    Extension(
        name = "src.cfuncs.libpaint",
        sources = ["src/cfuncs/libpaint.pyx"]
    ),

]

setup(
    name = "cfuncs",
    ext_modules = cythonize(extensions),
    include_dirs = [np.get_include()]
)
