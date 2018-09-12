# truffleboar

Search through git repositories and GitHub issues / pull requests for secrets.

This project is a somewhat fork/rewrite of the [truffleHog](https://github.com/dxa4481/truffleHog) project.

# Usage

Because truffleboar is dependent on a GitHub project, it requires the full project name (including organisation)

`truffleboar dxa4481/truffleHog`

# Development

1. Install a virtual environment

```
virtualenv venv -p python3.6
source ./venv/bin/activate
```

2. Install requirements
```
pip install -r requirements.txt
```
