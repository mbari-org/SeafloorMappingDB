# Base the build off of recent stable GDAL image
FROM osgeo/gdal:ubuntu-small-3.3.0 as python

# Python build stage
FROM python as python-build-stage

ARG BUILD_ENVIRONMENT=local

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
  -r local.txt


# Python 'run' stage
FROM python as python-run-stage

ARG BUILD_ENVIRONMENT=local
ARG APP_HOME=/app

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV BUILD_ENV ${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

# Install required system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y \
  graphviz \
  graphviz-dev \
  # psycopg2 dependencies
  libpq-dev \
  # Translations dependencies
  gettext \
  postgresql-client \
  python3-pip \
  # For quicker SeafloorMapping file finds
  mlocate \
  # Install here rather than from .devcontainer/devcontainer.json
  git less wget zsh ssh-client \
  # cleaning up unused files
  && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
  && rm -rf /var/lib/apt/lists/*

# All absolute dir copies ignore workdir instruction. All relative dir copies are wrt to the workdir instruction
# copy python dependency wheels from python-build-stage
COPY --from=python-build-stage /usr/src/app/wheels  /wheels/
COPY --from=python-build-stage /usr/lib/libgdal* /usr/lib/
RUN ldconfig

# use wheels to install python dependencies
RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
	&& rm -rf /wheels/

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint
RUN chmod +x /entrypoint

COPY ./compose/debug/django/start /start
RUN sed -i 's/\r$//g' /start
RUN chmod +x /start

RUN mkdir -p /media/thumbnails


# copy application code to WORKDIR
COPY . ${APP_HOME}

ENTRYPOINT ["/entrypoint"]
