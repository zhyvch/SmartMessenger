# 🚀 SmartMessenger

**A real-time messaging API with chat functionality, built for the ELEKS Python Internship Project.**

## 🛠️ Tech Stack

- ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) **FastAPI**
- ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white) **PostgreSQL**
- ![MongoDB](https://img.shields.io/badge/-MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white) **MongoDB**
- ![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker**
- ![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker Compose**
- ![UV](https://img.shields.io/badge/-UV-4B32C3?style=flat-square&logo=python&logoColor=white) **UV** (Python package installer)
- ![Uvicorn](https://img.shields.io/badge/-Uvicorn-009688?style=flat-square&logo=python&logoColor=white) **Uvicorn**

## 📋 Project Overview

SmartMessenger is a chat application backend that provides REST APIs for managing chats and messages, along with WebSocket support for real-time communication.

## 🔌 API Endpoints

### REST API

#### Chats
- `POST /chats` - Create a new chat
- `GET /chats/{chat_id}` - Retrieve a chat by ID
- `DELETE /chats/{chat_id}` - Delete a chat by ID
- `GET /chats/{chat_id}/messages` - Retrieve all messages for a specific chat

#### Messages
- `POST /messages` - Add a new message to a chat
- `GET /messages/{message_id}` - Retrieve a message by ID
- `DELETE /messages/{message_id}` - Delete a message by ID

#### AI
- `POST /ai/ask` - Get an AI response to a user query

#### Authentication (Розділити auth і users на різні роутери)
- `POST /auth/register` - Register a new user
- `GET /auth/verify-email` - Verify user email
- `POST /auth/login` - Login and get tokens
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and revoke token
- `DELETE /auth/users/me` - Delete user account
- `GET /auth/oauth/google/login` - Login with Google
- `GET /auth/oauth/google/callback` - Google OAuth callback

#### FRIEND REQUEST 
- `POST /requests` - Send friend request
- `POST /requests/{request_id}/accept` - Accept friend request
- `POST /requests/{request_id}/decline` - Decline friend request
- `DELETE /requests/{request_id}/delete` - Delete friend
- `GET /friends` - Friends list



### WebSocket API
- `WebSocket /chats/{chat_id}` - Establish a real-time connection to a specific chat

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Git

### Installation

1. Clone the repository:
```bash
    git clone https://github.com/your-username/SmartMessenger.git
    cd SmartMessenger
```

2. Create a `.env` file with the required environment variables:
```
DOCKER_RUN=true

API_HOST=127.0.0.1
API_PORT=8000

DEBUG=true

POSTGRES_USER=root
POSTGRES_PASSWORD=1234
POSTGRES_HOST=smart_messenger_postgres # Change to 127.0.0.1 if run locally without docker
POSTGRES_PORT=5672
POSTGRES_DB=users_db

MONGODB_USER=admin
MONGODB_PASSWORD=admin
MONGODB_HOST=smart_messenger_mongodb # Change to 127.0.0.1 if run locally without docker
MONGODB_PORT=27017
MONGODB_DB=chats_db

SECRET_KEY=my_super_secret_key

GOOGLE_CLIENT_ID=???
GOOGLE_CLIENT_SECRET=???

OPENAI_API_KEY=my_super_secret_openai_ai_key

```

3. Start the application:
```bash
  make app
```

4. Migrate the database:
```bash
  make revision-upgrade
```

## 🛠️ Makefile Commands

- `make app` - Start the application with Docker Compose
- `make app-down` - Stop the application and remove containers
- `make app-logs` - View application logs in real-time
- `make auto-revision` - Generate Alembic migration from model changes
- `make revision-upgrade` - Apply Alembic migrations to the database
- `make revision-downgrade` - Revert the last Alembic migration

## 🏗️ Architecture

SmartMessenger follows a clean architecture approach:
- **Entities**: Core business objects
- **Repositories**: Data access layer
- **Services**: Business logic
- **API**: REST and WebSocket interfaces

## 🧪 Development

### Project Structure
```
src/
├── api/
│   ├── main.py
│   ├── exception_handlers.py
│   └── v1/
│       ├── routers.py
│       └── websocket/
│           └── routers.py
├── apps/
│   ├── ai/
│   │   ├── dependencies.py
│   │   ├── prompts.py
│   │   ├── routers.py
│   │   ├── schemas.py
│   │   └── services.py
│   ├── chats/
│   │   ├── repositories/
│   │   │   ├── base.py
│   │   │   └── mongodb.py
│   │   ├── services/
│   │   │   ├── base.py
│   │   │   └── chats.py
│   │   ├── websocket/
│   │   │   ├── connections.py
│   │   │   └── routers.py
│   │   ├── converters.py
│   │   ├── converters.py
│   │   ├── dependencies.py
│   │   ├── entities.py
│   │   ├── exceptions.py
│   │   ├── models.py
│   │   ├── routers.py
│   │   └── schemas.py
│   └── users/
│       ├── dependencies.py
│       ├── models.py
│       ├── routers.py
│       ├── schemas.py
│       ├── security.py
│       └── utils.py
├── migrations/
├── settings/
│   └── config.py
└── databases.py
```

## 🐳 Docker Compose Services

- **smart_messenger**: Main API service running FastAPI
- **smart_messenger_postgres**: PostgreSQL database for structured data
- **smart_messenger_mongodb**: MongoDB database for chat messages

## 👥 Contributing

Contributors should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for creating commit messages:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semi-colons, etc)
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or correcting tests
- `build`: Changes to build process or tools
- `ci`: Changes to CI configuration
- `chore`: Other changes that don't modify src or test files

### Examples
```
feat: add chat notification feature
fix(api): handle missing user ID in request
docs: update installation instructions
refactor(database): optimize chat message queries
```

Breaking changes should be indicated by adding `!` after the type/scope or using a footer:
```
feat!: change API response format

feat(api): change response format
BREAKING CHANGE: API response now uses camelCase
```

## 📝 License

[MIT License](LICENSE)