PYCACHE_DIRS = $(shell find . -iname '__pycache__')
NODE_MODULES = $(shell find . -iname 'node_modules')
DIST = $(shell find . -iname 'dist')
VENV_DIRS = $(shell find . -iname '.venv')

.PHONY: tester
tester:
	echo $(PYCACHE_DIRS)

.PHONY: all
all: web api

.PHONY: install-uv
install-uv:
	@curl -LsSf https://astral.sh/uv/0.11.7/install.sh | sh

.PHONY: clean-api
clean-api:
	@cd api && uv clean && echo "Cleaned UV"
	@rm -rf $(PYCACHE_DIRS) $(VEND_DIRS) && echo "Cleaned pycache & venv"

.PHONY: clean-web
clean-web:
	@rm -rf $(NODE_MODULES) && echo "Cleaned node modules"

.PHONY: clean-dist
clean-dist:
	@rm -rf $(DIST) && echo "Cleaned dist"

.PHONY: clean
clean: clean-api clean-web clean-dist

.PHONY: api
api: api/dist
api/dist: web/dist
	mkdir -p api/src/makemkv_headless/ui
	cp -rv web/dist api/src/makemkv_headless/ui
	cd api && uv sync && uv build

.PHONY: web
web: web/dist
web/dist:
	cd web && npm ci && npm run build

.DEFAULT_GOAL := all

.PHONY: run-dev
run-dev: 
	./start.sh dev 4000 3000

.PHONY: release
release:
	gh workflow run --ref main release-create.yaml