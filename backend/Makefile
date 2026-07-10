
ifneq (,$(wildcard ../.env.dev))
    include ../.env.dev
    export
endif

.PHONY: lint
lint:
	ruff check --fix
	ruff format

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


.PHONY: alembic-upgrade-dack
alembic-upgrade-dack:
	POSTGRES_HOST=127.0.0.1 uv run alembic downgrade -1