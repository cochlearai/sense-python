import pathlib
from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="cochl-sense",
    version="1.1.0",
    description="Python Package for Cochlear.ai sense API ",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cochlearai/sense-python",
    author="Cochlear.ai",
    author_email="support@cochlear.ai",
    license="MIT License",
    classifiers=[
        "License :: OSI Approved :: MIT License",
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
