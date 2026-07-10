
ifneq (,$(wildcard ../.env.dev))
    include .env.dev
    export
endif


.PHONY: local
local:
	docker compose -f docker-compose.dev.yml --env-file .env.dev up -d --build --force-recreate --remove-orphans

.PHONY: alembic-upgrade
alembic-upgrade:
	docker exec -it backend uv run alembic upgrade head


.PHONY: alembic-upgrade-dack
alembic-upgrade-dack:
	docker exec -it backend uv run alembic downgrade -1