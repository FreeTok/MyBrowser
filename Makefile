GO ?= go

.PHONY: install test check

install:
	python3 scripts/install.py --go "$(GO)"

test:
	python3 -m unittest discover -s tests -p 'test_*.py'
	cd vendor/BrowseForge && $(GO) test ./cmd/server ./internal/api ./internal/browser ./internal/config ./internal/fingerprint ./internal/groups ./internal/humanize ./internal/mcp ./internal/profile ./internal/runtime ./internal/workflow

check:
	python3 scripts/check_repository.py
