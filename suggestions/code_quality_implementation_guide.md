# Code Quality Implementation Guide

This guide provides detailed instructions for implementing the code quality improvements in the improvement plan.

## 1. Add Input Validation

**Current Issue**: Some API endpoints have insufficient input validation, which could lead to invalid data and potential security issues.

**Implementation Steps**:

1. Update the `CreateChatSchema` in `src/apps/chats/schemas.py` to add more validation:

```python
class CreateChatSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    def to_entity(self, owner_id: int, is_group: bool) -> Chat:
        return Chat(
            name=self.name,
            is_group=is_group,
            owner_id=owner_id,
            member_ids=[owner_id]
        )
```

2. Update the `CreateMessageSchema` in `src/apps/chats/schemas.py` to add more validation:

```python
class CreateMessageSchema(BaseModel):
    content: str = Field(..., min_length=1, max_length=255 * 1024)

    def to_entity(self, chat_id: UUID, sender_id: int) -> Message:
        return Message(
            content=self.content,
            sender_id=sender_id,
            chat_id=chat_id,
        )
```

3. Update the `UpdateChatPermissionsSchema` in `src/apps/chats/schemas.py` to add more validation:

```python
class UpdateChatPermissionsSchema(BaseModel):
    can_send_messages: bool = Field(default=True)
    can_change_permissions: bool = Field(default=False)
    can_remove_members: bool = Field(default=False)
    can_delete_other_messages: bool = Field(default=False)
```

4. Add validation for query parameters in the `get_chat_messages` endpoint in `src/apps/chats/routers.py`:

```python
@chats_router.get(
    '/{chat_id}/messages',
    description='Retrieves messages for a chat with pagination.',
    status_code=status.HTTP_200_OK,
)
async def get_chat_messages(
    chat_id: UUID,
    service: ChatServiceDep,
    chat_member: ChatMemberDep,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
) -> ChatWithMessages:
    return ChatWithMessages(
        chat=await service.get_chat(chat_id),
        messages=await service.get_messages(chat_id, skip=skip, limit=limit),
    )
```

## 2. Add Unit Tests for Critical Components

**Current Issue**: The application lacks unit tests for critical components, which makes it difficult to ensure code reliability and prevent regressions when making changes.

**Implementation Steps**:

1. Create a new directory structure for tests:

```bash
mkdir -p tests/unit/apps/users
mkdir -p tests/unit/apps/chats
mkdir -p tests/unit/apps/posts
mkdir -p tests/unit/apps/ai
```

2. Add a `conftest.py` file in the `tests` directory to set up test fixtures:

```python
# tests/conftest.py
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi import FastAPI
from httpx import AsyncClient

from src.api.main import create_app
from src.apps.users.models import User
from src.apps.chats.entities import Chat, Message
from src.apps.chats.repositories import BaseChatRepository, BaseMessageRepository, BaseChatPermissionsRepository
from src.apps.chats.websocket.connections import ConnectionManager


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
async def async_client(app: FastAPI):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_user():
    return User(
        id=1,
        first_name="Test",
        last_name="User",
        email="test@example.com",
        username="testuser",
        is_active=True,
        email_verified=True
    )


@pytest.fixture
def mock_chat():
    return Chat(
        id="550e8400-e29b-41d4-a716-446655440000",
        name="Test Chat",
        is_group=False,
        owner_id=1,
        member_ids=[1, 2]
    )


@pytest.fixture
def mock_message():
    return Message(
        id="550e8400-e29b-41d4-a716-446655440001",
        content="Test message",
        sender_id=1,
        chat_id="550e8400-e29b-41d4-a716-446655440000",
        is_read=False,
        read_by=[]
    )


@pytest.fixture
def mock_chat_repo():
    repo = AsyncMock(spec=BaseChatRepository)
    return repo


@pytest.fixture
def mock_message_repo():
    repo = AsyncMock(spec=BaseMessageRepository)
    return repo


@pytest.fixture
def mock_chat_permissions_repo():
    repo = AsyncMock(spec=BaseChatPermissionsRepository)
    return repo


@pytest.fixture
def mock_connection_manager():
    manager = AsyncMock(spec=ConnectionManager)
    return manager
```

3. Create a test file for the authentication service:

```python
# tests/unit/apps/users/test_auth.py
import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import jwt

from src.apps.users.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    get_user_from_token
)
from src.settings.config import settings


def test_password_hashing():
    password = "testpassword"
    hashed = get_password_hash(password)

    # Verify the hash is different from the original password
    assert hashed != password

    # Verify the password can be verified against the hash
    assert verify_password(password, hashed)

    # Verify an incorrect password fails verification
    assert not verify_password("wrongpassword", hashed)


def test_create_access_token():
    user_id = 1
    expires_delta = timedelta(minutes=15)

    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=expires_delta
    )

    # Verify the token is a string
    assert isinstance(token, str)

    # Decode the token and verify the payload
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    assert "jti" in payload


def test_create_refresh_token():
    user_id = 1

    token = create_refresh_token(
        data={"sub": str(user_id)}
    )

    # Verify the token is a string
    assert isinstance(token, str)

    # Decode the token and verify the payload
    payload = jwt.decode(
        token,
        settings.SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )

    assert payload["sub"] == str(user_id)
    assert "exp" in payload
    assert "jti" in payload


@pytest.mark.asyncio
async def test_get_user_from_token_valid():
    user_id = 1
    token = create_access_token(data={"sub": str(user_id)})

    # Mock the database session and user query
    mock_session = AsyncMock()
    mock_user = AsyncMock()
    mock_user.id = user_id

    with patch("src.apps.users.security.get_async_db", return_value=mock_session):
        with patch("src.apps.users.security.User", return_value=mock_user):
            with patch("src.apps.users.security.select", return_value=mock_user):
                with patch("src.apps.users.security.RevokedToken.is_token_revoked", return_value=False):
                    user = await get_user_from_token(token)
                    assert user.id == user_id


@pytest.mark.asyncio
async def test_get_user_from_token_invalid():
    # Test with an expired token
    user_id = 1
    expires_delta = timedelta(minutes=-15)  # Expired 15 minutes ago
    token = create_access_token(
        data={"sub": str(user_id)},
        expires_delta=expires_delta
    )

    with pytest.raises(HTTPException) as excinfo:
        await get_user_from_token(token)

    assert excinfo.value.status_code == 401
```

4. Create a test file for the chat service:

```python
# tests/unit/apps/chats/test_chat_service.py
import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID

from fastapi import HTTPException

from src.apps.chats.services.chats import ChatService
from src.apps.ai.services import OpenAIService, UnsplashService


@pytest.mark.asyncio
async def test_get_chat(mock_chat_repo, mock_message_repo, mock_chat_permissions_repo, mock_connection_manager):
    # Arrange
    chat_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    mock_chat = AsyncMock()
    mock_chat_repo.get_chat.return_value = mock_chat

    service = ChatService(
        chat_repo=mock_chat_repo,
        message_repo=mock_message_repo,
        chat_permissions_repo=mock_chat_permissions_repo,
        connection_manager=mock_connection_manager,
        ai_service=AsyncMock(spec=OpenAIService),
        unsplash_service=AsyncMock(spec=UnsplashService)
    )

    # Act
    result = await service.get_chat(chat_id)

    # Assert
    assert result == mock_chat
    mock_chat_repo.get_chat.assert_called_once_with(chat_id)


@pytest.mark.asyncio
async def test_create_private_chat(mock_chat_repo, mock_message_repo, mock_chat_permissions_repo, mock_connection_manager):
    # Arrange
    mock_chat = AsyncMock()
    mock_chat.id = UUID("550e8400-e29b-41d4-a716-446655440000")
    mock_chat.owner_id = 1
    other_user_id = 2

    mock_chat_repo.get_private_chat_by_member_ids.return_value = None
    mock_chat_repo.get_chat.return_value = mock_chat

    service = ChatService(
        chat_repo=mock_chat_repo,
        message_repo=mock_message_repo,
        chat_permissions_repo=mock_chat_permissions_repo,
        connection_manager=mock_connection_manager,
        ai_service=AsyncMock(spec=OpenAIService),
        unsplash_service=AsyncMock(spec=UnsplashService)
    )

    # Act
    await service.create_private_chat(mock_chat, other_user_id)

    # Assert
    mock_chat_repo.get_private_chat_by_member_ids.assert_called_once_with(mock_chat.owner_id, other_user_id)
    mock_chat_repo.add_chat.assert_called_once_with(mock_chat)
    mock_chat_repo.get_chat.assert_called_once_with(mock_chat.id)
    assert mock_chat.save.called
    assert mock_chat_permissions_repo.add_user_chat_permissions.call_count == 2


@pytest.mark.asyncio
async def test_create_private_chat_with_self(mock_chat_repo, mock_message_repo, mock_chat_permissions_repo, mock_connection_manager):
    # Arrange
    mock_chat = AsyncMock()
    mock_chat.owner_id = 1

    service = ChatService(
        chat_repo=mock_chat_repo,
        message_repo=mock_message_repo,
        chat_permissions_repo=mock_chat_permissions_repo,
        connection_manager=mock_connection_manager,
        ai_service=AsyncMock(spec=OpenAIService),
        unsplash_service=AsyncMock(spec=UnsplashService)
    )

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.create_private_chat(mock_chat, mock_chat.owner_id)

    assert excinfo.value.status_code == 400
    assert "Users cannot create private chat with themselves" in excinfo.value.detail
```

5. Create a test file for the message service:

```python
# tests/unit/apps/chats/test_message_service.py
import pytest
from unittest.mock import AsyncMock, patch
from uuid import UUID

from fastapi import HTTPException

from src.apps.chats.services.chats import ChatService
from src.apps.ai.services import OpenAIService, UnsplashService


@pytest.mark.asyncio
async def test_get_message(mock_chat_repo, mock_message_repo, mock_chat_permissions_repo, mock_connection_manager):
    # Arrange
    chat_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    message_id = UUID("550e8400-e29b-41d4-a716-446655440001")

    mock_chat = AsyncMock()
    mock_message = AsyncMock()
    mock_message.chat_id = chat_id

    mock_chat_repo.get_chat.return_value = mock_chat
    mock_message_repo.get_message.return_value = mock_message

    service = ChatService(
        chat_repo=mock_chat_repo,
        message_repo=mock_message_repo,
        chat_permissions_repo=mock_chat_permissions_repo,
        connection_manager=mock_connection_manager,
        ai_service=AsyncMock(spec=OpenAIService),
        unsplash_service=AsyncMock(spec=UnsplashService)
    )

    # Act
    result = await service.get_message(chat_id, message_id)

    # Assert
    assert result == mock_message
    mock_chat_repo.get_chat.assert_called_once_with(chat_id)
    mock_message_repo.get_message.assert_called_once_with(message_id)


@pytest.mark.asyncio
async def test_get_message_wrong_chat(mock_chat_repo, mock_message_repo, mock_chat_permissions_repo, mock_connection_manager):
    # Arrange
    chat_id = UUID("550e8400-e29b-41d4-a716-446655440000")
    message_id = UUID("550e8400-e29b-41d4-a716-446655440001")

    mock_chat = AsyncMock()
    mock_message = AsyncMock()
    mock_message.chat_id = UUID("550e8400-e29b-41d4-a716-446655440002")  # Different chat_id

    mock_chat_repo.get_chat.return_value = mock_chat
    mock_message_repo.get_message.return_value = mock_message

    service = ChatService(
        chat_repo=mock_chat_repo,
        message_repo=mock_message_repo,
        chat_permissions_repo=mock_chat_permissions_repo,
        connection_manager=mock_connection_manager,
        ai_service=AsyncMock(spec=OpenAIService),
        unsplash_service=AsyncMock(spec=UnsplashService)
    )

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await service.get_message(chat_id, message_id)

    assert excinfo.value.status_code == 400
    assert f"Message with id {message_id} is not present in chat with id {chat_id}" in excinfo.value.detail
```

6. Update the `pyproject.toml` file to include pytest configuration:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_functions = "test_*"
asyncio_mode = "auto"
```

## 3. Add Error Handling for External Services

**Current Issue**: The application has limited error handling for external service calls (OpenAI and Unsplash), which could lead to unexpected behavior when these services fail.

**Implementation Steps**:

1. Create a new file `src/apps/ai/exceptions.py` to define custom exceptions for AI services:

```python
from fastapi import HTTPException, status


class AIServiceException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail
        )


class OpenAIServiceException(AIServiceException):
    def __init__(self, detail: str = "OpenAI service is currently unavailable"):
        super().__init__(detail=detail)


class UnsplashServiceException(AIServiceException):
    def __init__(self, detail: str = "Unsplash service is currently unavailable"):
        super().__init__(detail=detail)
```

2. Update the `OpenAIService` in `src/apps/ai/services.py` to improve error handling:

```python
import logging
from openai import OpenAI
from openai.error import OpenAIError, RateLimitError, APIError, AuthenticationError

from src.apps.ai.exceptions import OpenAIServiceException

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self, client: OpenAI):
        self.client = client

    async def ask(self, question: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ],
                max_tokens=150
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {str(e)}")
            raise OpenAIServiceException("OpenAI rate limit exceeded. Please try again later.")
        except AuthenticationError as e:
            logger.error(f"OpenAI authentication error: {str(e)}")
            raise OpenAIServiceException("Authentication error with OpenAI service.")
        except APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIServiceException("OpenAI API error. Please try again later.")
        except OpenAIError as e:
            logger.error(f"OpenAI error: {str(e)}")
            raise OpenAIServiceException(f"Error communicating with OpenAI: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI service: {str(e)}")
            raise OpenAIServiceException("Unexpected error occurred while processing your request.")
```

3. Update the `UnsplashService` in `src/apps/ai/services.py` to improve error handling:

```python
import logging
import httpx
from src.apps.ai.exceptions import UnsplashServiceException

logger = logging.getLogger(__name__)

class UnsplashService:
    def __init__(self, access_key: str):
        self.access_key = access_key
        self.base_url = "https://api.unsplash.com"

    async def search_photo(self, query: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/photos",
                    params={
                        "query": query,
                        "per_page": 1
                    },
                    headers={
                        "Authorization": f"Client-ID {self.access_key}"
                    },
                    timeout=10.0  # Set a reasonable timeout
                )

                response.raise_for_status()  # Raise exception for 4XX/5XX responses

                data = response.json()
                if not data.get("results") or len(data["results"]) == 0:
                    return f"No photos found for query: {query}"

                return data["results"][0]["urls"]["regular"]

        except httpx.TimeoutException:
            logger.error(f"Timeout while searching Unsplash for: {query}")
            raise UnsplashServiceException("Unsplash service timed out. Please try again later.")
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.error(f"HTTP error {status_code} from Unsplash: {str(e)}")

            if status_code == 401:
                raise UnsplashServiceException("Authentication error with Unsplash service.")
            elif status_code == 403:
                raise UnsplashServiceException("Access forbidden to Unsplash service.")
            elif status_code == 429:
                raise UnsplashServiceException("Unsplash rate limit exceeded. Please try again later.")
            else:
                raise UnsplashServiceException(f"Unsplash service error (HTTP {status_code}).")
        except Exception as e:
            logger.error(f"Unexpected error in Unsplash service: {str(e)}")
            raise UnsplashServiceException("Unexpected error occurred while processing your request.")
```

4. Update the chat service to handle these exceptions gracefully:

```python
async def create_message(self, message: Message) -> None:
    logger.info('Creating message to chat with id \'%s\'', message.chat_id)
    check_chat_exists = await self.get_chat(message.chat_id)

    await self.message_repo.add_message(message)
    await self.connection_manager.send_all(message.chat_id, message.content.encode())

    if message.content.lower().startswith("@ai"):
        question = message.content[3:].strip()

        try:
            answer = await self.ai_service.ask(question)
        except OpenAIServiceException as e:
            answer = f"Error while querying AI: {e.detail}"
            logger.error(answer)
        except Exception as e:
            answer = f"Unexpected error while querying AI: {str(e)}"
            logger.error(answer)

        ai_message = Message(
            chat_id=message.chat_id,
            sender_id="777",
            content=answer,
        )

        await self.message_repo.add_message(ai_message)
        await self.connection_manager.send_all(ai_message.chat_id, ai_message.content.encode())

    elif message.content.lower().startswith("@photo"):
        query = message.content[6:].strip()

        try:
            photo_url = await self.unsplash_service.search_photo(query)
        except UnsplashServiceException as e:
            photo_url = f"Error while getting photo: {e.detail}"
            logger.error(photo_url)
        except Exception as e:
            photo_url = f"Unexpected error while getting photo: {str(e)}"
            logger.error(photo_url)

        photo_message = Message(
            chat_id=message.chat_id,
            sender_id="777",
            content=photo_url,
        )

        await self.message_repo.add_message(photo_message)
        await self.connection_manager.send_all(photo_message.chat_id, photo_message.content.encode())
```

## Testing

After implementing these code quality improvements, test the application to ensure everything works as expected:

1. Test the input validation by sending invalid data to the endpoints:
```bash
# Test with an empty chat name
curl -X POST "http://localhost:8000/api/v1/chats/group" -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d '{"name": ""}'

# Test with an empty message content
curl -X POST "http://localhost:8000/api/v1/chats/{chat_id}/messages" -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d '{"content": ""}'
```

2. Run the unit tests:
```bash
pytest
```

3. Test the error handling for external services:
```bash
# Test with an invalid OpenAI API key
# Temporarily modify the .env file to use an invalid API key
curl -X POST "http://localhost:8000/api/v1/ai/ask" -H "Authorization: Bearer YOUR_TOKEN" -H "Content-Type: application/json" -d '{"question": "What is the capital of France?"}'

# Test with an invalid Unsplash API key
# Temporarily modify the .env file to use an invalid API key
curl -X GET "http://localhost:8000/api/v1/ai/photo?query=mountains" -H "Authorization: Bearer YOUR_TOKEN"
```

## 4. Add Pre-commit Hooks

**Current Issue**: The project lacks automated code quality checks and formatting, which can lead to inconsistent code style and quality issues.

**Implementation Steps**:

1. Install pre-commit:

```bash
pip install pre-commit
```

2. Create a `.pre-commit-config.yaml` file in the project root:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.10.0
    hooks:
      - id: ruff
        args:
          - --fix
      - id: ruff-format

  - repo: https://github.com/astral-sh/uv-pre-commit
    rev: 0.5.29
    hooks:
      - id: uv-lock
      - id: uv-export
        args:
          - --no-hashes
          - --output-file=requirements.txt
```

3. Update the `pyproject.toml` file to include ruff configuration:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "B", "I"]
ignore = []

[tool.ruff.format]
quote-style = "single"
indent-style = "space"
line-ending = "auto"
```

4. Initialize pre-commit:

```bash
pre-commit install
```

5. Run pre-commit on all files:

```bash
pre-commit run --all-files
```

### Explanation of Hooks

1. **pre-commit-hooks**:
   - `trailing-whitespace`: Removes trailing whitespace at the end of lines
   - `end-of-file-fixer`: Ensures files end with a newline
   - `check-yaml`: Validates YAML files
   - `check-added-large-files`: Prevents large files from being committed

2. **ruff-pre-commit**:
   - `ruff`: A fast Python linter that checks for errors and enforces style
   - `ruff-format`: A fast Python formatter that ensures consistent code style

3. **uv-pre-commit**:
   - `uv-lock`: Locks dependencies using uv (a faster alternative to pip)
   - `uv-export`: Exports dependencies to requirements.txt

### Testing

After implementing pre-commit hooks, test them to ensure they work as expected:

1. Make some changes to Python files that violate the style rules (e.g., add trailing whitespace, use double quotes instead of single quotes).

2. Try to commit the changes:
```bash
git add .
git commit -m "Test pre-commit hooks"
```

3. Pre-commit should run automatically and either fix the issues or prevent the commit if issues can't be fixed automatically.

4. You can also run pre-commit manually:
```bash
pre-commit run --all-files
```
