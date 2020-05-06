import pathlib
from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "Readme.md").read_text()

# This call to setup() does all the work
setup(
    name="cochl-sense",
    version="1.0.0",
    description="Python Package for Cochlear.ai sense API ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cochlearai/sense-python",
    author="Cochlear.ai",
    author_email="support@cochlear.ai",
    license='Apache License 2.0',
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Intended Audience :: Developers"
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=["grpcio", "protobuf"],
)