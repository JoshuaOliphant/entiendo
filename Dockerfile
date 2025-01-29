FROM python:3.12-slim-bookworm

# Copy uv from the official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy the project into the image
WORKDIR /app
ADD . /app

# Sync the project dependencies using uv
RUN uv sync --frozen

# Expose the port the app runs on
EXPOSE 8000

# Required environment variables
ENV ANTHROPIC_API_KEY=""
ENV LOGFIRE_TOKEN=""

# Run the FastAPI app with uvicorn
# Note: Using src.main:app since our app is in the src directory
CMD ["uv", "run", "python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
