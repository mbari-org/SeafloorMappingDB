# Seafloor Mapping Database

_Make MBARI seafloor mapping datasets more accessible and useful_

![smdb tests](https://github.com/mbari-org/SeafloorMappingDB/actions/workflows/ci.yml/badge.svg)
[![Requirements Status](https://requires.io/github/MBARIMike/SeafloorMappingDB/requirements.svg?branch=main)](https://requires.io/github/MBARIMike/SeafloorMappingDB/requirements/?branch=main)

### Text from the proposal

MBARI has now conducted hundreds of Mapping AUV missions and several dozen
low altitude survey ROV dives. Much of the resulting data have value to others
in the MBARI community, but the survey data and data products are only
accessible to those with both knowledge of where the data are stored, how they
are organized, and how to run the software used to process the data in maps,
images, and GIS objects. In order to make the Mapping AUV and LASS survey data
more accessible, we propose to capture metadata such as geographic location and
server storage paths in a relational database with a queryable web interface.
The envisioned system will utilize the same approach and open-source software
tools as the MBARI STOQS database for water-column data. This system can be
developed without changing the current file-based structure on the
SeafloorMapping share or impacting the work-flow for processing the sensor
data. The data will remain as files on the SeafloorMapping share on Titan.
Because the Titan server is web-accessible, metadata and data products can be
mined for populating the database and viewed through the query interface.

Seafloor mapping database: A relational database with geographic capability,
a geo-spatially enabled web query interface on Canyon Head, load scripts for
mining data from the SeafloorMapping archive, and user interfaces for testing
and manually adding data, will be built in Python with Django and PostgreSQL
using the PostGIS extension. The entire software stack is free and open source.

### Install a local development system using Docker

#### First time

Install [Docker](https://docker.io) and change directory to a location where
you will clone this repository. Clone the repo and start the services with
these commands:

```
# In your home directory or other preferred location copy the file locate database
mkdir docker_smdb_vol
scp smdb.shore.mbari.org:/opt/docker_smdb_vol/SeafloorMapping.db docker_smdb_vol
scp smdb.shore.mbari.org:/opt/docker_smdb_vol/exclude.list docker_smdb_vol
# cd to a development directory, e.g. ~/GitHub
git clone git@github.com:mbari-org/SeafloorMappingDB.git
cd SeafloorMappingDB
# Edit smdb/local.yml with fully qualified location of docker_smdb_vol
export SMDB_HOME=$(pwd)
export COMPOSE_FILE=$SMDB_HOME/smdb/local.yml
docker-compose up -d
docker-compose run --rm django python manage.py migrate
docker-compose run --rm django python manage.py createsuperuser
```

Then navigate to http://localhost:8000 to see the web application in local
development mode. Log into the admin interface using the credentials you
created in the last step above.

#### Thereafter

```
cd ${SMDB_HOME}
export COMPOSE_FILE=$SMDB_HOME/smdb/local.yml
# Shut down the services
docker-compose down
# Bring back up - must be done to use new edits, e.g. in scripts/load.py
docker-compose up -d --build
```

Mount `smb://titan.shore.mbari.org/SeafloorMapping` and load initial Mission data with:

```
# Replace <uid> with return from 'id -u'
docker-compose run --rm -u <uid> -v /Volumes/SeafloorMapping:/mbari/SeafloorMapping django scripts/load.py -v
```

### Work on the code with VS Code

1. Perform the [First time](https://github.com/mbari-org/SeafloorMappingDB#first-time)
   steps above.
   Install [VS Code](https://code.visualstudio.com/download) and the
   [Remote-Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
   extension.

2. From VS Code: File -> Open and select your SMDB_HOME directory. The `devcontainer.json`
   file will be detected and you will be prompted to "Reopen in Container". Click the button
   and wait for the containers to build and run.

3. To monitor the docker container logs in a terminal use the `debug.yml` configuration:

```
export COMPOSE_FILE=$SMDB_HOME/smdb/debug.yml
docker-compose logs -f
```

4. Use the debug launch configurations to Run and Debug the server, execute load.py, or run an
   IPython shell giving access through Django to the database. For example,
   In the Debug panel click the play button next to the "manage.py shell_plus" item in the pick list at top.
   A "In [1]:" prompt should appear in the Terminal pane - test by printing all the Missions in the database:

```
    In [1]: Mission.objects.all()
```

You may set breakpoints and examine variables in VS Code while the Python code is executing.

### Deploy a production instance of smdb

1. Clone the repository in a location on your production server with an account that can run docker, e.g.:

```
sudo -u docker_user -i
cd /opt
mkdir docker_smdb_vol && chown docker_user docker_smdb_vol
git clone git@github.com:mbari-org/SeafloorMappingDB.git
cd /opt/SeafloorMappingDB
export SMDB_HOME=$(pwd)
```

2. Acquire certificate files, name them smdb.crt, and smdb.key and place them in `${SMDB_HOME}/compose/production/traefik`

3. Start the app and load some data:

```
sudo -u docker_user -i
cd /opt/SeafloorMappingDB
export DOCKER_USER_ID=$(id -u)
export SMDB_HOME=$(pwd)
export COMPOSE_FILE=$SMDB_HOME/smdb/production.yml
docker-compose up -d
docker-compose run --rm django python manage.py migrate
docker-compose run --rm django python manage.py createsuperuser
# Replace <uid> with return from 'id -u'
docker-compose run --rm -u <uid> -v /mbari/SeafloorMapping:/mbari/SeafloorMapping django scripts/load.py -v
```

4. Navigate to https://smdb.shore.mbari.org (for example) to see the production web application.

5. To drop the database data and start over - use with caution:

```
docker-compose stop django
docker-compose exec postgres psql -U <dba> -d postgres
drop database smdb; \q
docker-compose down
docker volume rm $(docker volume ls -q)     # for good measure
git pull
docker-compose up -d --build
docker-compose run --rm django python manage.py makemigrations
docker-compose run --rm django python manage.py migrate
docker-compose run --rm django python manage.py createsuperuser
```
