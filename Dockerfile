FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy dependency files terlebih dahulu
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen

# Copy source code
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run application
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]