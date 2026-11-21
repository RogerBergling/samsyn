.PHONY: run test docker-build docker-run secret

run:
	python3 -m app

test:
	python3 -m unittest discover -s tests -v

docker-build:
	docker build -t ghcr.io/rogerbergling/verify:dev .

docker-run:
	docker run --rm -p 8080:8080 \
		-e AUTH_MODE=dev \
		-e SECRET_KEY=dev-only-change-me-please-32-chars-minimum \
		-e COOKIE_SECURE=0 \
		-e DATA_DIR=/data \
		-v samsyn-data:/data \
		ghcr.io/rogerbergling/verify:dev

secret:
	python3 -c "import secrets; print(secrets.token_urlsafe(48))"
