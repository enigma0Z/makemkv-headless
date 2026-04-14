

.PHONY: all
all: api/dist web/dist

.PHONY: clean
clean:
	@cd api && uv clean
	@find . -iname '.venv'        -exec rm -rf {} \; || echo "cleaned venvs"
	@find . -iname '__pycache__'  -exec rm -rf {} \; || echo "cleaned pycache"
	@find . -iname 'node_modules' -exec rm -rf {} \; || echo "cleaned node_modules"
	@find . -iname 'dist'         -exec rm -rf {} \; || echo "cleaned dist"

.PHONY: api
api: api/dist
api/dist:
	cd api && uv sync && uv build

.PHONY: web
web: web/dist
web/dist:
	cd web && npm ci && npm run build

.DEFAULT_GOL := all