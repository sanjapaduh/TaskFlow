# Focus TaskFlow  App

A lightweight task management application built with **FastAPI**, **PostgreSQL**, **SQLAlchemy 2** and a responsive vanilla JavaScript frontend.

Focus lets users create an account, sign in, and manage personal tasks with descriptions, completion status, importance levels and colored tags. The frontend is served directly by FastAPI, so no separate frontend server is required.

## Features

- JWT-based registration and authentication
- Personal todo lists isolated by user
- Create, edit, complete and delete tasks
- Importance levels from 0 to 10
- Colored task tags
- Search and status filters in the web interface
- Responsive UI for desktop and mobile
- Automatic database table creation on application startup
- Interactive API documentation via Swagger UI
- Redis-backed caching and session-related application data
- Full automated test suite covering API, authentication, database and frontend integration
- Docker Compose setup with PostgreSQL and Redis

## Tech Stack

- **Backend:** Python 3.13, FastAPI, Uvicorn
- **Database:** PostgreSQL 15
- **Cache and fast data store:** Redis 7
- **ORM:** SQLAlchemy 2 with async sessions
- **Authentication:** JWT, bcrypt
- **Frontend:** HTML, CSS and vanilla JavaScript
- **Testing:** pytest, async API and database tests
- **Dependency management:** Poetry
- **Deployment:** Docker and Docker Compose

## Project Structure

```text
.
├── main.py                 # FastAPI application and frontend entry point
├── database.py             # Async database engine and session dependency
├── models.py               # SQLAlchemy models
├── routers/
│   ├── auth.py             # Registration and authentication endpoints
│   ├── dependencies.py     # Shared FastAPI dependencies
│   ├── schemas.py          # Pydantic request schemas
│   ├── security.py         # Password hashing and JWT handling
│   └── todos.py             # Todo CRUD endpoints
├── static/
│   ├── index.html          # Frontend markup
│   ├── styles.css          # Application styles
│   └── app.js              # Frontend API integration and UI logic
├── tests/                  # Unit, integration and end-to-end tests
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── poetry.lock
```

## Quick Start with Docker

### 1. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+asyncpg://postgres:root@db:5432/postgres
REDIS_URL=redis://redis:6379/0
SECRET_KEY=replace-this-with-a-long-random-secret
```

Use a unique, long random value for `SECRET_KEY` outside local development. Do not commit `.env` or real secrets to the repository.

### 2. Start the application

```bash
docker compose up --build
```

The application will be available at:

- Web interface: <http://localhost:8080>
- Swagger UI: <http://localhost:8080/docs>
- ReDoc: <http://localhost:8080/redoc>

To stop the services:

```bash
docker compose down
```

To stop the services and remove the database volume:

```bash
docker compose down -v
```

The Docker Compose environment starts PostgreSQL and Redis together with the application. Redis is used for low-latency caching and temporary application data, while PostgreSQL remains the primary persistent data store.

## Local Development

### Prerequisites

- Python 3.13+
- Poetry
- PostgreSQL 15+
- Redis 7+

### Installation

Install dependencies:

```bash
poetry install
```

Set the environment variables for a locally running PostgreSQL instance:

```env
DATABASE_URL=postgresql+asyncpg://postgres:root@localhost:5432/postgres
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=replace-this-with-a-long-random-secret
```

Start the development server:

```bash
poetry run uvicorn main:app --reload
```

Open <http://localhost:8000> in a browser.

If you are using the included virtual environment directly on Windows:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

## API Reference

All protected todo routes require an HTTP header:

```http
Authorization: Bearer <access_token>
```

### Authentication

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/auth/create_user` | Create a user account |
| `POST` | `/auth/login-page` | Log in with a JSON request and receive a JWT |
| `POST` | `/auth/token` | OAuth2-compatible login endpoint |

Example registration request:

```json
{
  "username": "user1",
  "email": "user1@example.com",
  "password": "strong-password"
}
```

The username must contain at least one digit.

### Todos

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/todos/todos` | Get all tasks belonging to the current user |
| `GET` | `/todos/get/{item_id}` | Get one task by its user-specific number |
| `POST` | `/todos/addtodo` | Create a task |
| `PUT` | `/todos/change/item_id{item_id}` | Update a task |
| `DELETE` | `/todos/delete/todo:{item_id}` | Delete a task |

Create and update requests use the following JSON shape:

```json
{
  "todo_request": {
    "name": "Prepare presentation",
    "description": "Finish the slides",
    "done": false,
    "importance": 8,
    "tags": []
  },
  "tag": {
    "name": "work",
    "color": "BLUE"
  }
}
```

Supported tag colors are `RED`, `BLUE`, `GREEN` and `WHITE`.

## Database

The application creates the SQLAlchemy tables automatically when it starts. The main entities are:

- `users` — user accounts and password hashes
- `todos` — tasks owned by users
- `tags` — reusable task labels
- `task_tags` — many-to-many relationship between tasks and tags

For production environments, use a migration tool such as Alembic instead of relying on automatic table creation.

## Security Notes

- Keep `SECRET_KEY` outside source control.
- Use HTTPS when deploying outside a local environment.
- Use a strong database password in production.
- The default Docker credentials are intended for local development only.
- JWT access tokens are valid for 90 minutes.

## Redis

Redis is configured as the application's fast in-memory data store. It is used for cacheable and short-lived data, helping reduce repeated database reads and keep frequently accessed application data responsive.

The application expects the following environment variable:

```env
REDIS_URL=redis://localhost:6379/0
```

When running with Docker Compose, use `redis` as the hostname:

```env
REDIS_URL=redis://redis:6379/0
```

Redis data is intentionally treated as temporary. PostgreSQL remains the source of truth for users, tasks and tags, so removing the Redis volume does not remove the application's persistent data.

## Testing

The project includes a complete automated test suite for the main application layers:

- authentication, registration and JWT authorization;
- todo creation, retrieval, update and deletion;
- user data isolation;
- validation and error responses;
- PostgreSQL persistence and SQLAlchemy relationships;
- Redis-backed cache behavior;
- frontend/API integration flows.

Run the complete test suite with:

```bash
poetry run pytest
```

Run it with detailed output:

```bash
poetry run pytest -v
```

Run tests inside the Docker environment:

```bash
docker compose run --rm app poetry run pytest
```

The test suite should be run before opening a pull request or deploying a new version.

## Development Checks

Check Python syntax:

```bash
python -m compileall -q main.py routers
```

Check modified files for whitespace errors:

```bash
git diff --check
```

## License

No license has been specified for this project yet.
