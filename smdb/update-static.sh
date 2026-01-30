#!/bin/bash
# Script to update static files after making CSS/JS changes

set -e

echo "📦 Copying CSS files to container..."
docker cp ./smdb/static/css/project.css smdb_django_1:/app/staticfiles/css/project.css
docker cp ./smdb/static/css/leaflet-measure.css smdb_django_1:/app/staticfiles/css/leaflet-measure.css
docker cp ./smdb/static/css/map.css smdb_django_1:/app/staticfiles/css/map.css

echo "📦 Copying JS files to container..."
docker cp ./smdb/static/js/map.js smdb_django_1:/app/staticfiles/js/map.js

echo "📦 Copying templates to container..."
docker cp ./smdb/templates/pages/home.html smdb_django_1:/app/smdb/templates/pages/home.html

echo "🔄 Restarting Django to clear cache..."
docker restart smdb_django_1

echo "⏳ Waiting for Django to start..."
sleep 8

echo "✅ Static files updated! Site should be live at https://smdb-dev.shore.mbari.org/"
