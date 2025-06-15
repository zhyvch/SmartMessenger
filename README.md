# 🚀 SmartMessenger

**A real-time messaging API with social features, built for the ELEKS Python Internship Project.**
## 🛠️ Tech Stack

- ![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white) **Python**
- ![Pydantic](https://img.shields.io/badge/-Pydantic-005571?style=flat-square&logo=pydantic&logoColor=white) **Pydantic**
- ![FastAPI](https://img.shields.io/badge/-FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) **FastAPI**
- ![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-336791?style=flat-square&logo=postgresql&logoColor=white) **PostgreSQL**
- ![SQLAlchemy](https://img.shields.io/badge/-SQLAlchemy-FF0000?style=flat-square&logo=python&logoColor=white) **SQLAlchemy** (SQL ORM)
- ![MongoDB](https://img.shields.io/badge/-MongoDB-47A248?style=flat-square&logo=mongodb&logoColor=white) **MongoDB**
- ![Beanie](https://img.shields.io/badge/-Beanie-4B32C3?style=flat-square&logo=mongodb&logoColor=white) **Beanie** (MongoDB ODM)
- ![Docker](https://img.shields.io/badge/-Docker-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker**
- ![Docker Compose](https://img.shields.io/badge/-Docker%20Compose-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker Compose**
- ![UV](https://img.shields.io/badge/-UV-4B32C3?style=flat-square&logo=python&logoColor=white) **UV** (Python package installer)
- ![Uvicorn](https://img.shields.io/badge/-Uvicorn-009688?style=flat-square&logo=python&logoColor=white) **Uvicorn**

## 📋 Project Overview

SmartMessenger is a comprehensive social platform backend that provides REST APIs for managing chats, posts, comments, and user interactions, along with WebSocket support for real-time communication.

## 🔌 API Endpoints

### REST API

#### Authentication
- `POST /api/v1/auth/register` - Register a new user
- `GET /api/v1/auth/verify-email` - Verify user email
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and revoke token
- `GET /api/v1/auth/oauth/google/login` - Login with Google
- `GET /api/v1/auth/oauth/google/callback` - Google OAuth callback

#### Users
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update current user profile
- `DELETE /api/v1/users/me` - Delete user account

#### Posts
- `GET /api/v1/posts` - Get current user's posts
- `GET /api/v1/posts/{post_id}` - Get post by ID
- `POST /api/v1/posts` - Create a new post
- `PATCH /api/v1/posts/{post_id}` - Update a post
- `DELETE /api/v1/posts/{post_id}` - Delete a post
- `GET /api/v1/posts/{post_id}/comments` - Get post comments
- `POST /api/v1/posts/{post_id}/comments` - Add a comment to a post
- `GET /api/v1/posts/{post_id}/likes` - Get post likes
- `POST /api/v1/posts/{post_id}/likes` - Like a post
- `DELETE /api/v1/posts/{post_id}/likes` - Unlike a post

#### Comments
- `GET /api/v1/comments/{comment_id}` - Get comment by ID
- `PATCH /api/v1/comments/{comment_id}` - Update a comment
- `DELETE /api/v1/comments/{comment_id}` - Delete a comment

#### Chats
- `POST /api/v1/chats/private/{user_id}` - Create a private chat
- `POST /api/v1/chats/group` - Create a group chat
- `GET /api/v1/chats/{chat_id}` - Get chat by ID
- `DELETE /api/v1/chats/{chat_id}` - Delete a chat
- `GET /api/v1/chats/{chat_id}/messages` - Get chat messages
- `POST /api/v1/chats/{chat_id}/messages` - Add a message to chat
- `GET /api/v1/chats/{chat_id}/messages/{message_id}` - Get message by ID
- `DELETE /api/v1/chats/{chat_id}/messages/{message_id}` - Delete a message
- `POST /api/v1/chats/{chat_id}/members` - Add a member to chat
- `DELETE /api/v1/chats/{chat_id}/members/{user_id}` - Remove member from chat
- `PATCH /api/v1/chats/{chat_id}/members/{user_id}/permissions` - Update member permissions

#### Friends
- `POST /friends/requests` - Send friend request
- `POST /friends/requests/{request_id}/accept` - Accept friend request
- `POST /friends/requests/{request_id}/decline` - Decline friend request
- `DELETE /friends/requests/{request_id}` - Delete friend
- `GET /friends` - Friends list

#### AI Features
- `POST /api/v1/ai/ask` - Get an AI response to a query
- `GET /api/v1/ai/photo` - Search for photos from Unsplash

### WebSocket API
- `WebSocket /api/v1/chats/{chat_id}` - Real-time chat connection

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

2. Create a `.env` file with the required environment variables (see `.env.example`):

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
│   │   ├── services/
│   │   ├── websocket/
│   │   ├── dependencies.py
│   │   ├── entities.py
│   │   ├── routers.py
│   │   └── schemas.py
│   ├── posts/
│   │   ├── dependencies.py
│   │   ├── models.py
│   │   ├── routers/
│   │   │   ├── posts.py
│   │   │   └── comments.py
│   │   └── schemas.py
│   └── users/
│       ├── dependencies.py
│       ├── models.py
│       ├── routers/
│       │   ├── auth.py
│       │   └── users.py
│       ├── schemas.py
│       └── security.py
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

Contributors should follow the [Conventional Commits](https://www.conventionalcommits.org/) specification for creating commit messages.

## 📝 License

[MIT License](LICENSE)