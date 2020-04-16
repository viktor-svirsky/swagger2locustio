import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.rst").read_text()

# This call to setup() does all the work
setup(
    name="swagger2locustio",
    version="1.0.0",
    description="",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/vsvirsky/swagger2locustio",
    author="",
    author_email="",
    license="",
    keywords="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    packages=["swagger2locustio"],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "Jinja2==2.11.1",
    ],
    entry_points={
        "console_scripts": [
            "swagger2locustio=swagger2locustio.__main__:main",
        ]
    },
)
