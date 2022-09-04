import os.path as osp
import pathlib
import setuptools


PATH = pathlib.Path(__file__).parent

with open(osp.join(PATH, "README.md"), "r") as fh:
    LONG_DESCRIPTION = fh.read()

with open(osp.join(PATH, "requirements.txt"), "r") as fin:
    REQUIRED_PACKAGES = fin.read()

setuptools.setup(
    name="sdrl",
    version="0.0.1",
    author="geoyee",
    author_email="geoyee@yeah.net",
    description="Satellite Data Read Library",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    url="https://github.com/geoyee/SDRL",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=REQUIRED_PACKAGES,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
