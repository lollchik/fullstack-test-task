
ifneq (,$(wildcard ../.env.dev))
    include ../.env.dev
    export
endif

.PHONY: lint
lint:
	ruff check --fix
	ruff format

.PHONY: test
test:
	uv run pytest -vv

.PHONY: uv-sync
uv-sync:
	rm -rf uv.lock
	uv sync

.PHONY: alembic-revision
alembic-revision:
	POSTGRES_HOST=127.0.0.1 uv run alembic revision --autogenerate


.PHONY: alembic-upgrade
alembic-upgrade:
	POSTGRES_HOST=127.0.0.1 uv run alembic upgrade head

# почитать что куда по апгрейду и дауну
.PHONY: alembic-upgrade-dack
alembic-upgrade-dack:
	POSTGRES_HOST=127.0.0.1 uv run alembic downgrade -1