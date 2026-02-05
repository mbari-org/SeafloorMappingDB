#!/bin/bash
# Watch for CSS file changes and hot-reload them to the container
# Usage: ./watch-css.sh

set -e

WATCH_DIR="./smdb/static/css"
CONTAINER_NAME="smdb_django_1"

echo "🔍 Watching for CSS changes in $WATCH_DIR"
echo "📦 Will automatically copy to $CONTAINER_NAME"
echo "⚡ HOT-RELOAD ENABLED - No restart needed!"
echo ""
echo "Press Ctrl+C to stop watching..."
echo ""

# Initial copy to ensure we're in sync
echo "📋 Initial sync..."
docker cp ./smdb/static/css/project.css $CONTAINER_NAME:/app/staticfiles/css/project.css
docker cp ./smdb/static/css/leaflet-measure.css $CONTAINER_NAME:/app/staticfiles/css/leaflet-measure.css
docker cp ./smdb/static/css/map.css $CONTAINER_NAME:/app/staticfiles/css/map.css
echo "✅ Initial sync complete!"
echo ""

# Watch for changes using inotifywait
if ! command -v inotifywait &> /dev/null; then
    echo "❌ inotifywait not found. Installing inotify-tools..."
    sudo apt-get update && sudo apt-get install -y inotify-tools
fi

# Monitor for file modifications
inotifywait -m -e modify,create,close_write $WATCH_DIR --format '%w%f' |
while read FILE
do
    FILENAME=$(basename "$FILE")
    TIMESTAMP=$(date '+%H:%M:%S')
    echo "[$TIMESTAMP] 📝 Detected change: $FILENAME"
    
    # Copy the changed file to the container
    if docker cp "$FILE" "$CONTAINER_NAME:/app/staticfiles/css/$FILENAME" 2>/dev/null; then
        echo "[$TIMESTAMP] ✅ Hot-reloaded: $FILENAME"
    else
        echo "[$TIMESTAMP] ⚠️  Failed to copy: $FILENAME"
    fi
    echo ""
done
