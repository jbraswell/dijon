lint:
	poetry run isort --profile black ./dijon
	poetry run flake8 ./dijon

test:
	poetry run pytest ./dijon

docker:
	docker buildx build --platform linux/amd64 -f Dockerfile -t dijon .