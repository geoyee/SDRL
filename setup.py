import setuptools


with open("README.md", "r", encoding="utf-8") as fh:
    LONG_DESCRIPTION = fh.read()

with open("requirements.txt", "r") as fin:
    REQUIRED_PACKAGES = fin.read()

setuptools.setup(
    name="sdrl",
    version="0.0.5",
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
