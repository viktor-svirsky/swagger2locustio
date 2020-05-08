# swagger2locustio

<p align="center">
    <a href="https://pypi.org/project/swagger2locustio/" alt="PyPi Version">
        <img src="https://img.shields.io/pypi/v/swagger2locustio.svg" />
    </a>
    <a href="https://pypi.org/project/swagger2locustio/" alt="Python Versions">
        <img src="https://img.shields.io/pypi/pyversions/swagger2locustio.svg" />
    </a>
    <!--a href="" alt="Coverage">
        <img src="" />
    </a-->
    <a href="https://github.com/vsvirsky/swagger2locustio/LICENSE" alt="MIT License">
        <img src="https://img.shields.io/github/license/vsvirsky/swagger2locustio" />
    </a>
    <!--a href="" alt="Docs">
        <img src="" />
    </a-->
    <a href="https://github.com/vsvirsky/swagger2locustio/issues/" alt="Issues">
        <img src="https://img.shields.io/github/issues/vsvirsky/swagger2locustio" />
    </a>
    <a href="https://github.com/vsvirsky/swagger2locustio/issues/" alt="Pull Requests">
        <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat" />
    </a>
    <!--a href="" alt="Contributors">
        <img src="" />
    </a-->
    <a href="https://github.com/vsvirsky/swagger2locustio" alt="Github actions">
        <img src="https://github.com/vsvirsky/swagger2locustio/workflows/Python package/badge.svg" />
    </a>
    <a href="https://github.com/pre-commit/pre-commit" alt="pre-commit">
        <img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white" />
    </a>
</p>

swagger2locustio - a tool for testing API endpoints that have Open API / Swagger specifications using locustio.

It generates `locustfile.py` from the application schema.

## Supported specification versions:

- Swagger 2.x

## Installation

To install swagger2locustio via ``pip`` run the following command:

```bash
pip install swagger2locustio
```


## Usage

#### Command line options

```
usage: swagger2locustio [-h] -f SWAGGER_FILE [-r RESULTS_PATH] [-v] [-s {0,1,2}]
                        [-o {get,post,put,patch,delete,head,options,trace} [{get,post,put,patch,delete,head,options,trace} ...]]
                        [--paths-white PATHS_WHITE [PATHS_WHITE ...]] [--paths-black PATHS_BLACK [PATHS_BLACK ...]] [--tags-white TAGS_WHITE [TAGS_WHITE ...]]
                        [--tags-black TAGS_BLACK [TAGS_BLACK ...]]

optional arguments:
  -h, --help            show this help message and exit
  -f SWAGGER_FILE, --swagger-file SWAGGER_FILE
                        path to swagger file (default: None)
  -r RESULTS_PATH, --results-path RESULTS_PATH
                        path to store locustfile.py (default: generated)
  -v, --verbose         verbose (default: False)
  -s {0,1,2}, --strict-level {0,1,2}
                        add paths with required params without default values to locust tests (default: 2)
  -o {get,post,put,patch,delete,head,options,trace} [{get,post,put,patch,delete,head,options,trace} ...], --operations {get,post,put,patch,delete,head,options,trace} [{get,post,put,patch,delete,head,options,trace} ...]
                        operations to use in api testing (default: ['get'])
  --paths-white PATHS_WHITE [PATHS_WHITE ...], --pw PATHS_WHITE [PATHS_WHITE ...]
                        paths to use in api testing (default: [])
  --paths-black PATHS_BLACK [PATHS_BLACK ...], --pb PATHS_BLACK [PATHS_BLACK ...]
                        paths not to use in api testing (default: [])
  --tags-white TAGS_WHITE [TAGS_WHITE ...], --tw TAGS_WHITE [TAGS_WHITE ...]
                        tags to use in api testing (default: [])
  --tags-black TAGS_BLACK [TAGS_BLACK ...], --tb TAGS_BLACK [TAGS_BLACK ...]
                        tags to use in api testing (default: [])
```

## Contributing

Please, see the `CONTRIBUTING.md` file for more details.

## License

The code in this project is licensed under `MIT license`.
By contributing to `swagger2locustio`, you agree that your contributions
will be licensed under its MIT license.
