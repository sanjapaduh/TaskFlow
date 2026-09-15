# Use Python 3.13 to match your local environment
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port
EXPOSE 8080

# Start the FastAPI server (pointing directly to main.py in the root)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]