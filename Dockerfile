FROM python:3.13-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Disable virtualenv creation - Docker containers don't need them
RUN poetry config virtualenvs.create false

# Copy ONLY dependencies first to leverage Docker layer caching
COPY pyproject.toml poetry.lock ./

# The crucial fix: --no-root installs dependencies ONLY, skipping the project itself
RUN poetry install --no-interaction --no-ansi --no-root

# Now copy the rest of your application code
COPY . .

EXPOSE 8080

# Because we disabled virtualenvs, we can run uvicorn directly without 'poetry run'
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]