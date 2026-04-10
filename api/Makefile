PYTHON_VERSION := $(shell cat pyproject.toml | grep 'requires-python' | cut -d\" -f2 | cut -d\  -f2)
PYTHON := python$(PYTHON_VERSION)
VENV := .venv$(PYTHON_VERSION)

.PHONY: venv
venv: $(VENV)
$(VENV):
	uv venv

.PHONY: build
build: dist
dist: $(VENV)
	uv build

.PHONY: clean
clean:
	rm -rf .venv dist

.PHONY: build
build: dist

.PHONY: install
install:
	$(VENV)/bin/pip install -e .