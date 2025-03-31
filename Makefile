up:
	docker compose -f docker-compose.yaml up -d

down:
	docker compose -f docker-compose.yaml down

stop:
	docker  compose -f  docker-compose.yaml stop

start:
	docker  compose -f  docker-compose.yaml start