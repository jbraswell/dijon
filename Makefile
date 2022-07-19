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

.PHONY: publish
publish: docker
	docker tag dijon:latest bmltenabled/dijon:latest
	docker push bmltenabled/dijon:latest

.PHONY: build_publish_multi
build_publish_multi:
	docker buildx build --platform linux/amd64,linux/arm64 -f Dockerfile -t bmltenabled/dijon:latest . --push
