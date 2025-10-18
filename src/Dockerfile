FROM python:3.13-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create a non-root user and group for better security and storage management
RUN groupadd -r appuser && useradd -m -g appuser appuser

# Create working directory and set permissions
WORKDIR /src
RUN chown appuser:appuser /src

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry as the appuser
USER appuser
RUN curl -sSL https://install.python-poetry.org | python3 -

# Ensure Poetry is in the PATH for appuser
ENV PATH="/home/appuser/.local/bin:$PATH"

# Switch back to root for copying files and setting permissions
USER root
COPY pyproject.toml poetry.lock* ./

# Install dependencies and clean up cache
RUN poetry config virtualenvs.create false \
    && poetry install --no-root \
    && poetry cache clear pypi --all || true \
    && rm -rf ~/.cache/pip

# Copy the rest of the code
COPY . .

# Set permissions for persistent storage directories (e.g., media_root)
RUN mkdir -p /src/media_root && chown -R appuser:appuser /src/media_root

# Switch to non-root user
USER appuser