DC = docker compose
LOGS = docker logs
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
