# TaskFlow 🚀

TaskFlow is a robust, high-performance To-Do application API built with modern asynchronous Python. It provides secure task management with advanced relational tagging, utilizing a fully asynchronous database stack, Redis caching, and highly secure cookie-based authentication.

## 🛠️ Tech Stack

**Core Application:**
* **Framework:** [FastAPI](https://fastapi.tiangolo.com/) (Asynchronous REST API)
* **Language:** Python 3.10+
* **Authentication:** JWT (JSON Web Tokens) via secure `HttpOnly` Cookies
* **Password Hashing:** Passlib (`bcrypt`)

**Database & Data Management:**
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy 2.0 (Modern async operations)
* **Driver:** `asyncpg` (High-performance async PostgreSQL driver)
* **Migrations:** Alembic (Configured for async execution)
* **Caching / State:** Redis (For query caching, rate-limiting, or background task queues)

**Testing & Quality Assurance:**
* **Testing Framework:** `pytest`
* **Mocking:** `unittest.mock` (`AsyncMock`, `patch`) & FastAPI `TestClient`

---

## ✨ Key Features

* **Advanced Security:** Tokens are never exposed in JSON responses or local storage. JWTs are handled strictly through `HttpOnly`, `Secure`, and `SameSite=lax` cookies to protect against XSS and CSRF attacks.
* **Eager Loading Optimization:** Solves the N+1 database problem natively using SQLAlchemy's `joinedload` for seamless parent-child relationship queries (Tasks & Tags).
* **Async by Default:** From routing to database queries (`await db.scalar()`), the entire request lifecycle is non-blocking.
* **Robust Migration Tracking:** Database schema changes are strictly version-controlled using Alembic.
* **Redis Integration:** Ready for high-speed data retrieval and session management.

---

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10 or higher
* PostgreSQL installed and running
* Redis server installed and running

### 2. Installation
Clone the repository and install the dependencies:

```bash
git clone [https://github.com/yourusername/taskflow.git](https://github.com/yourusername/taskflow.git)
cd taskflow
python -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
