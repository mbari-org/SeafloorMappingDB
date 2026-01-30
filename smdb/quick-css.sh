#!/bin/bash
# Quick CSS update without restart
# IMPORTANT: Updates SOURCE and DESTINATION for Django ManifestStaticFilesStorage
# Usage: ./quick-css.sh

set -e

CONTAINER_NAME="smdb_django_1"
TIMESTAMP=$(date '+%H:%M:%S')

echo "⚡ Quick CSS Update (no restart)"
echo ""

# Copy CSS files to SOURCE directory (for collectstatic)
echo "[$TIMESTAMP] 📦 Copying CSS files to SOURCE..."
docker cp ./smdb/static/css/project.css $CONTAINER_NAME:/app/smdb/static/css/project.css
docker cp ./smdb/static/css/leaflet-measure.css $CONTAINER_NAME:/app/smdb/static/css/leaflet-measure.css  
docker cp ./smdb/static/css/map.css $CONTAINER_NAME:/app/smdb/static/css/map.css

# Copy CSS files to STATICFILES directory (for immediate serving)
echo "[$TIMESTAMP] 📦 Copying CSS files to STATICFILES..."
docker cp ./smdb/static/css/project.css $CONTAINER_NAME:/app/staticfiles/css/project.css
docker cp ./smdb/static/css/leaflet-measure.css $CONTAINER_NAME:/app/staticfiles/css/leaflet-measure.css  
docker cp ./smdb/static/css/map.css $CONTAINER_NAME:/app/staticfiles/css/map.css

# Find and update HASHED versions (Django ManifestStaticFilesStorage)
echo "[$TIMESTAMP] 🔍 Updating hashed CSS files..."

# Update hashed project.css
HASHED_PROJ=$(docker exec $CONTAINER_NAME sh -c "ls /app/staticfiles/css/project.*.css 2>/dev/null | grep -v '.gz' | head -1" || echo "")
if [ ! -z "$HASHED_PROJ" ]; then
    HASHED_FILENAME=$(basename "$HASHED_PROJ")
    echo "[$TIMESTAMP]    → Found: $HASHED_FILENAME"
    docker cp ./smdb/static/css/project.css $CONTAINER_NAME:"$HASHED_PROJ"
fi

# Update hashed leaflet-measure.css
HASHED_LM=$(docker exec $CONTAINER_NAME sh -c "ls /app/staticfiles/css/leaflet-measure.*.css 2>/dev/null | grep -v '.gz' | head -1" || echo "")
if [ ! -z "$HASHED_LM" ]; then
    HASHED_FILENAME=$(basename "$HASHED_LM")
    echo "[$TIMESTAMP]    → Found: $HASHED_FILENAME"
    docker cp ./smdb/static/css/leaflet-measure.css $CONTAINER_NAME:"$HASHED_LM"
fi

# Copy templates
echo "[$TIMESTAMP] 📦 Copying templates..."
docker cp ./smdb/templates/pages/home.html $CONTAINER_NAME:/app/smdb/templates/pages/home.html

echo ""
echo "[$TIMESTAMP] ✅ CSS updated to SOURCE and STATICFILES!"
echo "[$TIMESTAMP] 💡 For new hashes, run: ./update-static.sh"
echo "[$TIMESTAMP] 🌐 Refresh browser: Ctrl+Shift+R"
echo "[$TIMESTAMP] 🌐 https://smdb-dev.shore.mbari.org/"
