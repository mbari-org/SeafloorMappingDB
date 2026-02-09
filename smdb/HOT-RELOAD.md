# Hot-Reload CSS/Template Changes

## Quick CSS Update (Recommended)

For instant CSS updates **without** container restart:

```bash
cd /opt/SeafloorMappingDB/smdb
./quick-css.sh
```

- **Speed**: ~200ms (vs 18+ seconds with restart)
- **No downtime**: Django keeps running
- **Auto-updates**: CSS and templates copied directly to container

## Auto-Watch Mode (Advanced)

Automatically detect and hot-reload CSS changes as you save files:

```bash
cd /opt/SeafloorMappingDB/smdb
./watch-css.sh
```

This will:
1. Monitor `./smdb/static/css/` for file changes
2. Automatically copy changed files to the container
3. Display real-time notifications
4. **No restart needed!**

Press `Ctrl+C` to stop watching.

**Note**: Requires `inotify-tools` (will auto-install if missing)

## Full Update with Restart (Legacy)

If you need to restart Django (for JS changes, etc.):

```bash
cd /opt/SeafloorMappingDB/smdb
./update-static.sh
```

- **Speed**: ~18 seconds (includes Django restart)
- **Use when**: Changing JavaScript or need to clear Django cache

## Files Updated by Quick Scripts

### CSS Files:
- `smdb/static/css/project.css`
- `smdb/static/css/leaflet-measure.css`
- `smdb/static/css/map.css`

### Templates:
- `smdb/templates/pages/home.html`

## After Making Changes

1. **Edit your CSS file** (e.g., `smdb/static/css/leaflet-measure.css`)
2. **Run quick update**: `./quick-css.sh`
3. **Hard refresh browser**: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
4. **See changes immediately!**

## Troubleshooting

### Changes not appearing?

1. **Clear browser cache**: Do a hard refresh (`Ctrl+Shift+R`)
2. **Check container**: Verify file was copied:
   ```bash
   docker exec smdb_django_1 cat /app/staticfiles/css/leaflet-measure.css | head -20
   ```
3. **Force update**: Use `./update-static.sh` for full refresh

### Watch script not working?

Install inotify-tools:
```bash
sudo apt-get update && sudo apt-get install -y inotify-tools
```

## Cache-Busting

The `home.html` template includes cache-busting parameters:
```html
<link rel="stylesheet" href="{% static 'css/leaflet-measure.css' %}?{% now "U" %}&v=3">
```

This ensures browsers always fetch the latest version.
