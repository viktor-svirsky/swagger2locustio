## Installation

```bash
pip install -e .
pip install requirements_dev.txt
pre-commit install -t pre-commit
pre-commit install -t pre-push
```

## Run pre-commit hooks for all code

```bash
pre-commit run -a
```

## Run pre-push hooks for all code

```bash
pre-commit run -a --hook-stage push
```