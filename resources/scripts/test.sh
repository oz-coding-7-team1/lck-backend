set -eo pipefail

COLOR_GREEN=`tput setaf 2;`
COLOR_NC=`tput sgr0;` # No Color

echo "Starting black"
poetry run black .
echo "OK"

echo "Starting isort"
poetry run isort .
echo "OK"

echo "Starting mypy"
poetry run mypy .
echo "OK"

echo "Starting test with coverage"
poetry run coverage run manage.py test
poetry run coverage report -m

echo "${COLOR_GREEN}All tests passed successfully!${COLOR_NC}"