# Healthcare Data Processing Pipeline
# Author: Hope Donglo - OpenClassrooms (DataSoluTech)

FROM python:3.13-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock README.md ./

# Copy source code
COPY src/ ./src/

# Copy data files
COPY data/ ./data/

# Install dependencies (no virtual environment in container)
RUN poetry config virtualenvs.create false && \
    poetry install --only main

# Set Python path
ENV PYTHONPATH=/app

# Run pipeline
CMD ["python", "-m", "csv_containerisation_mongodb.main.main"]