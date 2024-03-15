FROM node:10-stretch-slim as client-builder

ARG DOCKER_USER_ID
ARG APP_HOME=/app
WORKDIR ${APP_HOME}

COPY ./package.json ${APP_HOME}
RUN npm install && npm cache clean --force
COPY . ${APP_HOME}
RUN npm run build

# Base the build off of recent stable GDAL image
FROM osgeo/gdal:ubuntu-small-3.6.2 as python

ARG DOCKER_USER_ID

# Python build stage
FROM python as python-build-stage

ARG DOCKER_USER_ID
ARG BUILD_ENVIRONMENT=production

# Install apt packages
RUN apt-get update && apt-get install --no-install-recommends -y \
  # dependencies for building Python packages
  build-essential \
  graphviz-dev \
  # psycopg2 dependencies
  libpq-dev \
  python3-dev \
  python3-pip

# Requirements are installed here to ensure they will be cached.
COPY ./requirements .

# Create Python Dependency and Sub-Dependency Wheels.
RUN pip wheel --wheel-dir /usr/src/app/wheels  \
  -r ${BUILD_ENVIRONMENT}.txt


# Python 'run' stage
FROM python as python-run-stage

ARG DOCKER_USER_ID
ARG BUILD_ENVIRONMENT=production
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN addgroup --system django \
    && adduser --system --ingroup django django

RUN adduser docker_user --ingroup django --uid $DOCKER_USER_ID


# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  graphviz \
  graphviz-dev \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  # For quicker SeafloorMapping file finds
  mlocate \
  postgresql-client \
  python3-pip \
  ssh-client \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/
RUN ldconfig

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
  && rm -rf /wheels/


COPY --chown=docker_user:django ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint


COPY --chown=docker_user:django ./compose/production/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start


# copy application code to WORKDIR
# - for some reason project.css isn't copied from APP_HOME, copy separately
COPY --from=client-builder --chown=docker_user:django ${APP_HOME} ${APP_HOME}
COPY ./smdb/static/css/project.css /app/smdb/static/css/

RUN mkdir -p /media/thumbnails /media/logs
RUN chown docker_user:django /media/thumbnails /media/logs

# make django owner of the WORKDIR directory as well.
RUN chown docker_user:django ${APP_HOME}

USER docker_user

ENTRYPOINT ["/entrypoint"]
