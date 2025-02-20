#!/bin/bash

source ~/.bashrc

export DJANGO_SETTINGS_MODULE=config.settings.prod

# 데이터베이스 마이그레이션
echo "Applying database migrations..."
poetry run python manage.py migrate --no-input

# 정적 파일 수집
echo "Collecting static files..."
poetry run python manage.py collectstatic --no-input

# Gunicorn 실행
echo "Starting Gunicorn..."
exec poetry run gunicorn config.wsgi:application --bind 0.0.0.0:8000