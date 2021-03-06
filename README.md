# Jeopardy

A Python application for creating and playing Jeopardy games.

## Pre-requisites

* Docker
* Docker-compose
* Google oauth credentials
* Create RSA key pair

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
  * http://localhost
  * http://127.0.0.1
* Authorized redirect URIs:
  * http://localhost/user/oauth2callback
  * http://127.0.0.1/user/oauth2callback

### Create RSA Key Pair

```bash
openssl genrsa -out jwt-rsa256 4096
openssl rsa -in jwt-rsa256 -pubout > jwt-rsa256.pub
```

## Development

The application can be run locally via Docker:
```bash
git clone git@github.com:lekha/jeopardy
cd jeopardy
cp .env.example .env
# modify .env file to have appropriate secrets
docker network create secure-docker-socket
docker-compose build
docker-compose run --rm --workdir /database backend yoyo apply
docker-compose up ingress
curl http://127.0.0.1/health-check
```

## Tests

Tests can be run locally via Docker:
```bash
docker-compose -f docker-compose.test.yml build
docker-compose -f docker-compose.test.yml up test_backend
```

## Database

### Run migrations

To apply:

```bash
docker-compose run --rm --workdir /database backend yoyo apply
```

To rollback:

```bash
docker-compose run --rm --workdir /database backend yoyo rollback
```

To see migration status:

```bash
docker-compose run --rm --workdir /database backend yoyo list
```
