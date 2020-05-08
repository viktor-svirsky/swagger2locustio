import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="swagger2locustio",
    version="0.0.3",
    python_requires=">=3.7",
    description="Tool for testing API endpoints that have Open API / Swagger specifications using locustio",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/vsvirsky/swagger2locustio",
    author="",
    author_email="",
    license="MIT",
    keywords="",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=["swagger2locustio"],
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        "Jinja2==2.11.2",
        "PyYAML==5.3.1",
        "coloredlogs==14.0"
    ],
    entry_points={
        "console_scripts": [
            "swagger2locustio=swagger2locustio.__main__:main",
        ]
    },
)
