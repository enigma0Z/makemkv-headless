.venv312:
	python3.12 -m venv .venv312
	.venv312/bin/pip install -r requirements.txt

dist: .venv312
	.venv312/bin/python3 -m build

.PHONY: clean
clean:
	rm -rf .venv312 dist

.PHONY: self-install
self-install:
	.venv312/bin/pip install -e .