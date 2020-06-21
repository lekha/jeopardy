# Jeopardy

A Python application for creating and playing Jeopardy games.

## Pre-requisites

* Docker
* Docker-compose

## Development

The application can be run locally via Docker:
```bash
git clone git@github.com:lekha/jeopardy
cd jeopardy
docker-compose build
docker-compose run --rm web yoyo apply
docker-compose up web
curl http://0.0.0.0:8000/health-check
```

## Database

### Run migrations

To apply:

```bash
docker-compose run --rm --workdir /app/database web yoyo apply
```

To rollback:

```bash
docker-compose run --rm --workdir /app/database web yoyo rollback
```

To see migration status:

```bash
docker-compose run --rm --workdir /app/database web yoyo list
```
