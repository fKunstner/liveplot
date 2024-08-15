### Dev Readme

**The Devtools** used are `isort`, `black`, `mypy`, `pytest` and `pylint`.
Their configuration is in `pyproject.toml`
and the `Makefile` provides helpers to run everything
(`make test`, `make format`, `make lint`).
`make check` runs the linters without modifications.

**The entrypoint for the CLI** is specified in `pyproject.toml` as 
```
[project.scripts]
liveplot = "liveplot.cli:main"
```

**The tests** check some of the interactions with matplotlib/pyplot 
and can open/close figures when running.

