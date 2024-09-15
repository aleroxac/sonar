## ---------- UTILS
.PHONY: help
help: ## Show this menu
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean
clean: ## Clean all cache and reports files
	@sudo rm -rf sonar.json .coverage coverage.xml testsuite.xml .pytest_cache
	@docker rm -f sonar 2> /dev/null

.PHONY: install
install: # Install requirements
	@[ ! -e /usr/bin/virtualenv ] && python -m pip install --break-system-packages virtualenv || true
	@if [ ! -e .venv ]; then \
		python -m virtualenv .venv; \
		source .venv/bin/activate; \
		pip install -r requirements.txt; \
		pip install -r requirements-dev.txt; \
	fi



## ---------- MAIN
.PHONY: activate
activate: ## Activate the virtualenv
	@. .venv/bin/activate

.PHONY: run
run: activate ## Run the application
	@python src/main.py

.PHONY: test
test: activate ## Run unit-tests
	@python -m pytest \
		--cov=src \
		--cov-config=coverage.ini \
		--cov-report=xml \
		--junitxml=testsuite.xml
	@$(call replace_path_on_coverage_file)
