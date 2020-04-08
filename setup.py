import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="swagger2locustio",
    version="1.0.0",
    description="",
    long_description=README,
    long_description_content_type="text/markdown",
    url="",
    author="",
    author_email="",
    license="",
    keywords="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["swagger2locustio"],
    zip_safe=False,
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "swagger2locustio=swagger2locustio.__main__:main",
        ]
    },
)
