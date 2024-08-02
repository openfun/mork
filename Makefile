# -- General
SHELL := /bin/bash

# -- Docker
COMPOSE          = bin/compose
COMPOSE_RUN      = $(COMPOSE) run --rm --no-deps
COMPOSE_RUN_API = $(COMPOSE_RUN) api

# -- MySQL
EDX_DB_HOST = mysql
EDX_DB_PORT = 3306

# -- Postgresql
DB_HOST = postgresql
DB_PORT = 5432

# -- Mork
MORK_IMAGE_NAME         ?= mork
MORK_IMAGE_TAG          ?= development
MORK_IMAGE_BUILD_TARGET ?= development
MORK_SERVER_PORT        ?= 8100
MORK_TEST_DB_NAME       ?= test-mork-db

# -- Celery
MORK_CELERY_SERVER_PORT		?= 5555


# ==============================================================================
# RULES

default: help

.env:
	cp .env.dist .env

.git/hooks/pre-commit:
	ln -sf ../../bin/git-hook-pre-commit .git/hooks/pre-commit

git-hook-pre-commit:  ## Install git pre-commit hook
git-hook-pre-commit: .git/hooks/pre-commit
	@echo "Git pre-commit hook linked"
.PHONY: git-hook-pre-commit

# -- Docker/compose
bootstrap: ## bootstrap the project for development
bootstrap: \
  .env \
  build \
  run \
  seed-edx-database
.PHONY: bootstrap

build: ## build the app containers
build: \
  build-docker-api
.PHONY: build

build-docker-api: ## build the api container
build-docker-api: .env
	MORK_IMAGE_BUILD_TARGET=$(MORK_IMAGE_BUILD_TARGET) \
	MORK_IMAGE_NAME=$(MORK_IMAGE_NAME) \
	MORK_IMAGE_TAG=$(MORK_IMAGE_TAG) \
	  $(COMPOSE) build api
.PHONY: build-docker-api

down: ## stop and remove all containers
	@$(COMPOSE) down
.PHONY: down

logs: ## display frontend/api logs (follow mode)
	@$(COMPOSE) logs -f api
.PHONY: logs

logs-celery: ## display celery logs (follow mode)
	@$(COMPOSE) logs -f celery
.PHONY: logs-celery

purge-celery: ## purge celery tasks
	@$(COMPOSE_EXEC) celery celery -A mork.celery_app purge
.PHONY: purge-celery

flower: ## run flower
	@$(COMPOSE_EXEC) celery celery -A mork.celery_app flower
.PHONY: flower

run: ## run the whole stack
run: \
	run-api \
	run-celery
.PHONY: run

run-celery: ## run the celery server (development mode)
	@$(COMPOSE) up -d celery
	@echo "Waiting for celery to be up and running..."
	@$(COMPOSE_RUN) dockerize -wait tcp://$(DB_HOST):$(DB_PORT) -timeout 60s
.PHONY: run-api

run-api: ## run the api server (development mode)
	@$(COMPOSE) up -d api
	@echo "Waiting for api to be up and running..."
	@$(COMPOSE_RUN) dockerize -wait tcp://api:$(MORK_SERVER_PORT) -timeout 60s
.PHONY: run-api

status: ## an alias for "docker compose ps"
	@$(COMPOSE) ps
.PHONY: status

stop: ## stop all servers
	@$(COMPOSE) stop
.PHONY: stop

seed-edx-database:  ## seed the edx database with test data
	@echo "Waiting for mysql to be up and running…"
	@$(COMPOSE_RUN) dockerize -wait tcp://$(EDX_DB_HOST):$(EDX_DB_PORT) -timeout 60s
	@echo "Seeding the edx database…"
	@$(COMPOSE) exec -T celery python /opt/src/seed_edx_database.py
.PHONY: seed-experience-index

# -- Provisioning
create-test-db: ## create API test database
	@$(COMPOSE) exec postgresql bash -c 'psql "postgresql://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$(DB_HOST):$(DB_PORT)/postgres" -c "create database \"$(MORK_TEST_DB_NAME)\";"' || echo "Duly noted, skipping database creation."
.PHONY: create-api-test-db

drop-test-db: ## drop API test database
	@$(COMPOSE) exec postgresql bash -c 'psql "postgresql://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$(DB_HOST):$(DB_PORT)/postgres" -c "drop database \"$(MORK_TEST_DB_NAME)\";"' || echo "Duly noted, skipping database deletion."
.PHONY: drop-api-test-db


migrate:  ## run alembic database migrations for the mork database
	@echo "Running database engine…"
	@$(COMPOSE) up -d postgresql
	@$(COMPOSE_RUN) dockerize -wait tcp://$(DB_HOST):$(DB_PORT) -timeout 60s
	@echo "Create mork service database…"
	@$(COMPOSE) exec postgresql bash -c 'psql "postgresql://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$(DB_HOST):$(DB_PORT)/postgres" -c "create database \"mork\";"' || echo "Duly noted, skipping database creation."
	@echo "Running migrations for mork service…"
	@bin/alembic upgrade head
.PHONY: migrate

# -- Linters

lint: ## lint python sources
lint: \
  lint-black \
  lint-ruff
.PHONY: lint

lint-black: ## lint python sources with black
	@echo 'lint:black started…'
	@$(COMPOSE_RUN_API) black --config pyproject.toml src/mork tests
.PHONY: lint-black

lint-ruff: ## lint python sources with ruff
	@echo 'lint:ruff started…'
	@$(COMPOSE_RUN_API) ruff check --config pyproject.toml .
.PHONY: lint-ruff

lint-ruff-fix: ## lint and fix python sources with ruff
	@echo 'lint:ruff-fix started…'
	@$(COMPOSE_RUN_API) ruff check --config pyproject.toml . --fix
.PHONY: lint-ruff-fix

## -- Tests

test: ## run api tests
test: \
  run \
  create-test-db
	bin/pytest
.PHONY: test


# -- Misc
help:
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'
.PHONY: help
