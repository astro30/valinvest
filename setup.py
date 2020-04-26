import setuptools
import os

here = os.path.abspath(os.path.dirname(__file__))
about = {}

with open(os.path.join(here, 'valinvest', '__version__.py'), 'r') as f:
    exec(f.read(), about)

with open("README.md", "r") as fh:
    readme = fh.read()

setuptools.setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    long_description=readme,
    long_description_content_type='text/markdown',
    author=about['__author__'],
    url=about['__url__'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
