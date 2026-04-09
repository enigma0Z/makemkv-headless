PYTHON_VERSION := 3.12

PYTHON := python$(PYTHON_VERSION)
VENV := .venv$(PYTHON_VERSION)

.PHONY: venv
venv: $(VENV)
$(VENV):
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -r requirements.txt

dist: $(VENV)
	$(VENV)/bin/python3 -m build

.PHONY: clean
clean:
	rm -rf $(VENV) dist

.PHONY: build
build: dist

.PHONY: install
install:
	$(VENV)/bin/pip install -e .