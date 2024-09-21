## ---------- UTILS
.PHONY: help
help: ## Show this menu
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: clean
clean: ## Clean all cache and reports files
	@sudo rm -rf sonar.json coverage.out
	@docker rm -f sonar 2> /dev/null

.PHONY: install
install: # Install requirements
	@go mod tidy



## ---------- MAIN
.PHONY: run
run: ## Run the application
	@go run main.go

.PHONY: test
test: ## Run unit-tests
	@go test ./... -covermode=atomic -coverprofile coverage.out
