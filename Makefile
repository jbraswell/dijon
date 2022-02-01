.PHONY: lint
lint:
	poetry run isort --profile black ./dijon
	poetry run flake8 ./dijon

.PHONY: test
test:
	poetry run pytest ./dijon

.PHONY: docker
docker:
	docker buildx build --platform linux/amd64 -f Dockerfile -t dijon .
