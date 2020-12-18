import setuptools

setuptools.setup(
    name="petromodder",
    version_config=True,
    author="Adam Cheng",
    author_email="tkc@equinor.com",
    description="Unofficial PetroMod API",
    long_description="Unofficial Python API for reading and writing PetroMod models",
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/petromodder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=["pandas>=1.0.0", "shapely>=1.6.3", "tabulate>=0.8.3"],
    python_requires=">=3.6",
    setup_requires=['setuptools-git-versioning'],
)
