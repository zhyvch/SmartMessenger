DC = docker compose
LOGS = docker logs
EXEC = docker exec -it
COMPOSE_FILE = docker-compose.yml
ENV = --env-file .env
APP_CONTAINER = smart_messenger


.PHONY: app
app:
	${DC} -f ${COMPOSE_FILE} ${ENV} up --build -d

.PHONY: app-down
app-down:
	${DC} -f ${COMPOSE_FILE} down

.PHONY: app-logs
app-logs:
	${LOGS} ${APP_CONTAINER} -f

.PHONY: auto-revision
auto-revision:
	${EXEC} ${APP_CONTAINER} alembic revision --autogenerate

.PHONY: revision-upgrade
revision-upgrade:
	${EXEC} ${APP_CONTAINER} alembic upgrade head

.PHONY: revision-downgrade
revision-downgrade:
	${EXEC} ${APP_CONTAINER} alembic downgrade -1

.PHONY: run-migrations
run-migrations:
	${DC} -f ${COMPOSE_FILE} ${ENV} up --build smart_messenger_migrations
