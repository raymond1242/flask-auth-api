compile-requirements:
	pip-compile requirements.in
install:
	pip install -r requirements.txt
run:
	python app.py
build:
	docker compose build
start:
	docker compose up -d
stop:
	docker compose down
database:
	docker-compose exec web python manage.py create_db
