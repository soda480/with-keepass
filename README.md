[![GitHub Workflow Status](https://github.com/soda480/with-keepass/workflows/ci/badge.svg)](https://github.com/soda480/with-keepass/actions)
[![PyPI version](https://badge.fury.io/py/with-keepass.svg)](https://badge.fury.io/py/with-keepass)
[![python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-teal)](https://www.python.org/downloads/)

# with-keepass

`with-keepass` is a command-line utility that allows you to run any command with environment variables automatically injected from a KeePass database.

This is especially useful for securely managing sensitive credentials (like API keys, AWS tokens, or database passwords) without hardcoding them into scripts, leaving them in plaintext in your shell history or exposing them in the parent shell.

### Why use `with-keepass`?

* **Ephemeral secrets**: Environment variables exist only for the lifetime of the executed process. They are not stored in your shell, not written to history, and vanish as soon as the command finishes.

* **Reduced risk**: Since the parent shell is never modified, secrets are isolated to the command being run and its child processes.

* **KeePass integration**: This lets you use an existing, trusted password manager as the single source of truth for sensitive data.

* **Practical workflow**: Instead of hardcoding secrets or exporting them manually, you inject them only when needed — making secret use explicit and controlled.

## Installation

```bash
pip install with-keepass
```

## Loading secrets from a KeePass `group` or KeePass `entry`

`with-keypass` is able to load environment variables from either a KeePass Group or KeePass Entry.

A KeePass `Group` contains multiple entries, where each entry:

Title → becomes the environment variable name.

The custom string field named value → becomes the environment variable value.

A KeePass `Entry` contains multiple custom string fields, where each field is treated as key value pair.

## Usage

`with-keypass` will prompt for the master password of the KeePass database.

```bash
usage: with-keypass [-h] [--db DB_PATH] [--path PATH] [--dry-run] ...

Execute a command with environment variables loaded from KeePass.

positional arguments:
  command       Command to execute; must be preceded by -- (not required with --dry-run)

options:
  -h, --help    show this help message and exit
  --db DB_PATH  Path to KeePass .kdbx database file (default: $HOME/.kp.kdbx)
  --path PATH   path to KeePass entry or KeePass group containing the secrets to load (default: EnvVars)
  --dry-run     Print NAME=value pairs and exit; do not exec a command (default: False)
```

## Examples

Run AWS CLI with injected credentials:
```bash
with-keypass --path AwsSecrets --field-name value -- \
    aws s3 ls
```

Preview environment variables:
```bash
with-keypass --dry-run
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

Run kubectl with secrets from a custom DB:
```bash
with-keepass --db "$HOME/.keepass/work.kdbx" --path 'Root/Secrets/K8s' -- \
    kubectl get pods --namespace=default
```

## Exit Codes
| Code | Description |
| :------- | :------ |
| 0 | Success |
| 1 | Runtime error (failed to open DB, etc.) |
| 2 | Usage error (bad arguments, group not found, no secrets) |
| 130 | User aborted (Ctrl-C or password prompt canceled) |


## Development

Create and source virtual environment:
```bash
python -m venv venv && source venv/Scripts/activate
```

Install project in editable mode:
```bash
python -m pip install -e .[dev]
```

Lint the source code:
```bash
python -m flake8 -v with_keepass/ --max-line-length 100 --ignore=E302,E305
```

Run unit tests:
```bash
python -m unittest discover tests/ -v
```

Compute coverage report:
```bash
python -m coverage run -m unittest discover tests/
python -m coverate report -m
```

Run cyclomatic complexity:
```bash
python -m radon cc -s with_keepass/
```

Run bandit scan:
```bash
python -m bandit -r with_keepass/ --skip B606
```

Build the package:
```bash
python -m build
```
