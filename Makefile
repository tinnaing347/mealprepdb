test:
	-docker compose run --rm -e MEALPREPDB_ENVIRONMENT=testing app ./test-runner.sh
	docker compose down

test-marker:
	-docker compose run --rm -e MEALPREPDB_ENVIRONMENT=testing app ./test-runner.sh -m $(marker) 
	docker compose down 

test-single-module:
	-docker compose run --rm -e MEALPREPDB_ENVIRONMENT=testing app ./test-runner.sh -n $(module) 
	docker compose down 

upgrade-head:
	-docker compose run --rm app alembic upgrade head
	docker compose down

downgrade-base:
	-docker compose run --rm app alembic downgrade base 
	docker compose down 

sql-migrate-upgrade: 
	-docker compose run --rm app alembic upgrade head --sql 
	docker compose down                      

