# 🚀 SmartMessenger

**A real-time messaging API with chat functionality, built for the ELEKS Python Internship Project.**

## 🛠️ Tech Stack

- ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) **FastAPI**
- ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white) **PostgreSQL**
- ![MongoDB](https://img.shields.io/badge/-MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white) **MongoDB**
- ![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker**
- ![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker Compose**
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

### WebSocket API
- `WebSocket /{chat_id}` - Establish a real-time connection to a specific chat

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
DEBUG=True

PG_USER=root
PG_PASSWORD=1234
PG_HOST=smart_messenger_postgres # Change to 127.0.0.1 if run locally without docker
PG_PORT=5672
PG_DATABASE=users_db

MONGODB_USER=admin
MONGODB_PASSWORD=admin
MONGODB_HOST=smart_messenger_mongodb # Change to 127.0.0.1 if run locally without docker
MONGODB_PORT=27017
MONGODB_DB=chats_db

```

3. Establishment of dependencies:
```bash
  pip install pdm
  pdm install
```

4. Start the application:
```bash
  make app  
```

5. Check application logs:
```bash
  make app-logs
```

6.  Stop the application:
```bash
  make app-down
```

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
│   └── v1/
│       ├── handlers.py
│       └── websocket/
│           └── handlers.py
├── apps/
│   ├── chats/
│   │   ├── converters/
│   │   ├── entities/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── schemas/
│   │   └── services/
│   └── users/
│       ├── 
│       ├── 
│       ├── 
│       ├── 
│       ├── 
│       └── 

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
