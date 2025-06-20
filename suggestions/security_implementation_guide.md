# Security Implementation Guide

This guide provides detailed instructions for implementing the security enhancements in the improvement plan.

## 1. Fix CORS Configuration

**Current Issue**: The CORS middleware is configured to allow all origins (`"*"`), which is a security risk in production.

**Implementation Steps**:

1. Update the CORS middleware in `src/api/main.py`:

```python
# Replace this:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # або ["http://localhost:8000"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# With this:
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        f"http://localhost:{settings.API_PORT}",
        f"http://127.0.0.1:{settings.API_PORT}",
        # Add other trusted origins here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

2. Consider adding a configuration setting for allowed origins in `src/settings/config.py`:

```python
# Add to Settings class
CORS_ORIGINS: list[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
```

Then update the middleware to use this setting:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

## 2. Implement Database Connection Cleanup

**Current Issue**: The lifespan context manager initializes MongoDB but doesn't properly close connections when the application shuts down.

**Implementation Steps**:

1. Update the lifespan function in `src/api/main.py`:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize connections
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_mongo(mongo_client)

    yield

    # Cleanup connections
    mongo_client.close()
    logging.info("MongoDB connection closed")
```

2. Update the `init_mongo` function in `src/databases.py` to accept a client:

```python
async def init_mongo(client: AsyncIOMotorClient = None):
    from src.apps.chats.models import ChatModel, MessageModel, ChatPermissionsModel

    if client is None:
        client = AsyncIOMotorClient(settings.MONGODB_URL)

    await init_beanie(
        database=client[settings.MONGODB_DB],
        document_models=[ChatModel, MessageModel, ChatPermissionsModel]
    )

    return client
```

## 3. Add Rate Limiting

**Current Issue**: There is no rate limiting to prevent abuse of the API.

**Implementation Steps**:

1. Install the required package:

```bash
pip install fastapi-limiter
```

2. Create a new file `src/api/rate_limiter.py`:

```python
import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter

from src.settings.config import settings

async def init_rate_limiter():
    """Initialize the rate limiter with Redis."""
    redis_client = redis.from_url(
        f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0", 
        encoding="utf-8", 
        decode_responses=True
    )
    await FastAPILimiter.init(redis_client)

# Rate limit decorator for routes
def rate_limit(times: int = 100, seconds: int = 60):
    """Rate limit decorator for routes."""
    return RateLimiter(times=times, seconds=seconds)
```

3. Update `src/settings/config.py` to include Redis settings:

```python
# Add to Settings class
REDIS_HOST: str = "localhost"
REDIS_PORT: int = 6379
```

4. Update the lifespan function in `src/api/main.py` to initialize the rate limiter:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize connections
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_mongo(mongo_client)

    # Initialize rate limiter
    if not settings.DEBUG:
        await init_rate_limiter()

    yield

    # Cleanup connections
    mongo_client.close()
    logging.info("MongoDB connection closed")
```

5. Apply rate limiting to sensitive endpoints in `src/apps/users/routers/auth.py` and other routers:

```python
from src.api.rate_limiter import rate_limit

@auth_router.post(
    '/login',
    dependencies=[Depends(rate_limit(times=5, seconds=60))],  # 5 attempts per minute
)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    # Existing code...
```

6. Update `docker-compose.yml` to include Redis:

```yaml
services:
  # Existing services...

  smart_messenger_redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: always

volumes:
  # Existing volumes...
  redis_data:
```

## 4. Add Database Migration Sidecar Service

**Current Issue**: Database migrations are currently run manually after the application is started, which can lead to inconsistencies between the application code and database schema during deployment.

**Implementation Steps**:

1. Create a new file `Dockerfile.migrations` for the migrations service:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements and install dependencies
COPY pyproject.toml .
COPY uv.lock .
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e .

# Copy application code
COPY . .

# Set environment variables
ENV PYTHONPATH=/app

# Create an entrypoint script
RUN echo '#!/bin/sh\n\
echo "Waiting for PostgreSQL to start..."\n\
sleep 5\n\
echo "Running database migrations..."\n\
alembic upgrade head\n\
echo "Migrations completed successfully."\n\
' > /app/run-migrations.sh && chmod +x /app/run-migrations.sh

# Set the entrypoint
ENTRYPOINT ["/app/run-migrations.sh"]
```

2. Update the `docker-compose.yml` file to add the migrations service:

```yaml
  smart_messenger_migrations:
    build:
      context: .
      dockerfile: Dockerfile.migrations
    container_name: smart_messenger_migrations
    env_file:
      - .env
    depends_on:
      - smart_messenger_postgres
    restart: "no"
```

3. Update the main service to depend on the migrations service:

```yaml
  smart_messenger:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: smart_messenger
    env_file:
      - .env
    ports:
      - '${API_PORT}:8000'
    command: 'uvicorn --factory api.main:create_app --host 0.0.0.0 --port 8000 --reload'
    depends_on:
      - smart_messenger_postgres
      - smart_messenger_mongodb
      - smart_messenger_migrations
    volumes:
      - ./src:/app/src
    restart: unless-stopped
```

4. Update the Makefile to include a command for running migrations separately:

```makefile
.PHONY: run-migrations
run-migrations:
	${DC} -f ${COMPOSE_FILE} ${ENV} up --build smart_messenger_migrations
```

## Testing

After implementing these security enhancements, test the application to ensure everything works as expected:

1. Start the application with Docker Compose:
```bash
make app
```

2. Test the CORS configuration by making requests from different origins.

3. Test the database migration sidecar service:
   - Check the logs to ensure migrations ran successfully:
   ```bash
   docker logs smart_messenger_migrations
   ```
   - Verify that the database schema is up-to-date by connecting to the PostgreSQL database:
   ```bash
   docker exec -it smart_messenger_postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "\dt"
   ```
   - Test the separate migration command:
   ```bash
   make run-migrations
   ```

4. Test the rate limiting by making multiple requests to protected endpoints.