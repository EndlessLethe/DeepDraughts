from setuptools import setup
from Cython.Build import cythonize
from Cython.Compiler import Options
import numpy, os

setup(
    name='Draughts env app',
    ext_modules=cythonize("cython_env.pyx", compiler_directives={'language_level': 3}),
    include_dirs=[numpy.get_include()],
    zip_safe=False,
)