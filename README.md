# Jeopardy

A Python application for creating and playing Jeopardy games.

## Pre-requisites

* Docker
* Docker-compose
* Google oauth credentials

### Create Google OAuth Credentials

1. Log in at https://console.cloud.google.com.
2. Create a new project.
3. Configure the OAuth consent screen (hamburger menu: _APIs & Services_ -->
   _OAuth consent screen_).
4. Create new OAuth client ID credentials (hamburger menu: _APIs & Services_
   --> _Credentials_).
5. Store the newly generated client ID and secret values in the .env file.

For local development, these settings work well:

* Application type: web application
* Authorized JavaScript origins:
  * http://localhost:8000
  * http://127.0.0.1:8000
* Authorized redirect URIs:
  * http://localhost:8000/oauth2callback
  * http://127.0.0.1:8000/oauth2callback

## Development

The application can be run locally via Docker:
```bash
git clone git@github.com:lekha/jeopardy
cd jeopardy
cp .env.example .env
# modify .env file to have appropriate secrets
docker-compose build
docker-compose run --rm --workdir /database backend yoyo apply
docker-compose up backend
curl http://127.0.0.1:8000/health-check
```

## Database

### Run migrations

To apply:

```bash
docker-compose run --rm --workdir /database backend yoyo apply
```

To rollback:

```bash
docker-compose run --rm --workdir /database web yoyo rollback
```

To see migration status:

```bash
docker-compose run --rm --workdir /database web yoyo list
```
