import setuptools

setuptools.setup(
    name="petromodder",
    version_config={
        "template": "{tag}",
        "dev_template": "{tag}",
        "dirty_template": "{tag}",
        "starting_version": "0.0.1",
        "version_callback": None,
        "version_file": None,
        "count_commits_from_version_file": False,
    },
    author="Adam Cheng",
    author_email="tkc@equinor.com",
    description="Tools for manupulating PetroMod model",
    long_description="Tools for manupulating PetroMod model. PetroMod is a registered trademark of Schlumberger",
    long_description_content_type="text/markdown",
    url="https://github.com/equinor/petromodder",
    packages=["petromodder"],
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "pandas>=1.0.0",
        "shapely>=1.6.3",
        "tabulate>=0.8.3",
        "xtgeo>=2.14.1",
    ],
    python_requires=">=3.7,<=3.9.7",
    setup_requires=["setuptools-git-versioning"],
)
