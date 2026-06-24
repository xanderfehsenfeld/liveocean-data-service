# Liveocean Data Service

Application and database to fetch, transform, store, and serve data from University of Washington's [LiveOcean](https://faculty.washington.edu/pmacc/LO/LiveOcean.html) service.

## Prerequisites

- `uv` [python package manager](https://github.com/astral-sh/uv)
- Either
  - `docker` if you want to run the database locally
  - `cloud-sql-proxy` if you want to proxy to a google cloud sql instance.

## Setup/install

1. Create a file `.env` in root with the following structure. Replace the variable values:

```shell
POSTGRES_USER=<username>
POSTGRES_PW=<password>
POSTGRES_DB=pg4django
PGADMIN_MAIL=<email>
PGADMIN_PW=<admin password>


PG_USER=<username>
PG_PSWD=<password>
PG_DB_NAME=pg4django
PG_HOST_DEV=0.0.0.0  # cannot be pg host when run django within docker
PG_HOST=0.0.0.0 # local ip for postgres
PG_PORT=5432

SECRET_KEY=<A secret key for the django app>
DATABASE_URL=postgres://<username>:<password>@//cloudsql/<google cloud sql endpoint>
```

2. `docker compose up` to start the database service, and wait for it to finish starting. OR start the Cloud Sql proxy: `cloud-sql-proxy <google cloud project id>:<region>:<cloud sql instance name>`.
3. `uv sync` to install python packages.
4. `uv run --env-file=.env python manage.py migrate` to apply migrations.

## Run development server in docker container

Run the following command to build and run the docker container. May take awhile on the first time to build.

`docker run -p 8080:8080 --rm -it $(docker build -q .)`

## Run in local environment

After ensuring the database is instance is up and running, run the following commands:

1. This command is only needed on first run or if a migration is needed: `uv run --env-file=.env python manage.py migrate`

2. Run the development server `uv run --env-file=.env python manage.py runserver`

# Implementation details

## Database

Dockerized Postgres + PostGIS

## Service

Django + GeoDjango

## Development and helpful scripts

### Run tests

```shell
#Run tests
uv run --env-file=.env python manage.py test

#Run and watch tests with entr

find . -name '*.py' | entr -c uv run --env-file=.env python manage.py test
```

### Regenerate fixture data. Usually only necessary after changing database schema

```shell
uv run --env-file=.env python manage.py dumpdata \
    --indent=4 \
    --natural-foreign \
    --natural-primary \
    > world/fixtures/one-forecast.json
```

## Helpful resources

- https://www.baeldung.com/java-geospatial-applications#2-geospatial-standards-ogc-geoapi
- https://www.mongodb.com/docs/manual/geospatial-queries/
- https://faculty.washington.edu/pmacc/LO/tracks2_PS.html
- https://medium.com/@emmanuelirekponor86/bridging-the-gap-combining-geography-with-web-development-full-stack-a-powerful-combination-for-01af6f2e7632
- [OSGeo GeoTools Java Library](https://www.osgeo.org/projects/geotools/)
- [PostGIS](https://postgis.net/)
- [Article able webGIS](https://www.lifeingis.com/most-popular-framework-for-back-end-webgis-development/)
- [Top Web Frameworks for WebGIS Development: Organized by Context](https://tierrainsights.buzz/top-web-frameworks-for-webgis-development-organized-by-context-a4547e8fafc4)
