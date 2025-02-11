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

# Install Poetry
RUN pip install --upgrade pip && pip install poetry
RUN poetry --version

# Copy project files
COPY . /app/

# Copy pyproject.toml and poetry.lock(의존성 파일 복사
COPY pyproject.toml poetry.lock /app/

# Install dependencies
# --no-interaction은 사용자 입력 요구 X, --no-ansi는 색상 제거 - 일부 터미널에서 이상해질 수 있음
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

# Expose port
EXPOSE 8000

# Start Gunicorn server
CMD ["gunicorn", "--workers=3", "--bind=0.0.0.0:8000", "config.wsgi:application"]
