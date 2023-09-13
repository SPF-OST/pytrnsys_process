import setuptools as _st

with open("README.md", "r") as fh:
    long_description = fh.read()


_st.setup(
    name="pytrnsys-process",
    version_config=True,
    packages=_st.find_packages(),
    author="Institute for Solar Technology (SPF), OST Rapperswil",
    author_email="damian.birchler@ost.ch",
    description="Post processing for pytrnsys",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pytrnsys.readthedocs.io",
    include_package_data=True,
    install_requires=["pandas"],
    package_data={
        "pytrnsys-process": ["py.typed"],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: Microsoft :: Windows",
    ],
    setup_requires=["setuptools-git-versioning"],
    python_requires=">=3.9",
)
