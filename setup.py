import setuptools

setuptools.setup(
    name="pyPMod",
    version="0.0.1",
    author="Adam Cheng",
    author_email="tkc@equinor.com",
    description="Unofficial PetroMod API",
    long_description="Unofficial Python API for reading and writing PetroMod models",
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/pyPMod",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas==1.0.0", "shapely==1.7.0", "numpy==1.18.1"],
    python_requires=">=3.6",
)
