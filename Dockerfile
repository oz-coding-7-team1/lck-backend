# Base image
FROM python:3.12.6

# Set environment variables
    #로그 즉시 출력
ENV PYTHONUNBUFFERED=1 \
    # pip 캐시 off
    PIP_NO_CACHE_DIR=off \
    # pip 패키지 설치 시 버전 확인 off
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치 및 PATH 설정
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Copy project files
COPY . /app/

# Copy pyproject.toml and poetry.lock(의존성 파일 복사)
COPY pyproject.toml /app/pyproject.toml
COPY poetry.lock /app/poetry.lock

# Install dependencies
RUN poetry install --no-root

# Expose port
EXPOSE 8000

# Start Gunicorn server
CMD ["bash", "resources/scripts/run.sh"]
