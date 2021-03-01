from setuptools import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext

ext = Extension("about_c", sources=["about_c.pyx"])

setup(ext_modules=[ext], cmdclass={"build_ext": build_ext})