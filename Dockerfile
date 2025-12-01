# 1. Builder Stage: Uses Python 3.11 (Stable and MCP-compatible version)
# We use a builder stage to keep the final image clean and small.
FROM python:3.11-slim as builder

# Define the working directory inside the container
WORKDIR /app

# Installs system dependencies required for the Python PostgreSQL client (psycopg2)
# and other build tools.
# libpq-dev is the header library needed to compile the psycopg2 client.
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Copies requirements file and installs Python packages (e.g., google-adk, python-dotenv)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Final Stage (Runtime): Uses a production-ready, minimalist image
FROM python:3.11-slim

# Defines the application directory
WORKDIR /app

# Copies only the installed Python packages (dependencies) from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
# Copies the entire application source code
COPY . /app

# Define the default command to run the application (optional, can be overridden by docker-compose)
# ENTRYPOINT ["python", "main.py"]
# Example command for integration testing: CMD ["python", "main.py", "dev"]