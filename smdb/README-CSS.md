# FOOLPROOF CSS Editing

## The Simple Way

Edit any CSS file, then run:

```bash
./css
```

That's it. Takes ~18 seconds.

## What It Does

1. ✅ Copies CSS to container
2. ✅ Runs collectstatic (regenerates hashed filenames)
3. ✅ Updates templates
4. ✅ No restart needed
5. ✅ Works every time

## Complete Workflow

```bash
cd /opt/SeafloorMappingDB/smdb

# Edit your CSS file
nano smdb/static/css/leaflet-measure.css

# Deploy changes
./css

# Hard refresh browser: Ctrl+Shift+R
```

## Files You Can Edit

- `smdb/static/css/leaflet-measure.css` - Leaflet measurement tool styling
- `smdb/static/css/project.css` - Main project styles
- `smdb/static/css/map.css` - Map-specific styles
- `smdb/templates/pages/home.html` - Home page template

All get deployed by `./css`

## How It Works

The `./css` script:
- Copies files to `/app/smdb/static/css/` (source)
- Runs `collectstatic` which:
  - Generates hashed filenames like `leaflet-measure.9ccf36ebeb9e.css`
  - Updates the manifest so Django knows which hash to use
  - Copies everything to `/app/staticfiles/`
- Django serves the updated files immediately

## Browser Cache

The `?{% now "U" %}` parameter in templates cache-busts on every page load:
```html
<link href="{% static 'css/leaflet-measure.css' %}?{% now "U" %}">
```

This timestamp ensures browsers always check for updates.

## Troubleshooting

**CSS not updating?**
1. Hard refresh: `Ctrl+Shift+R` (clears browser cache)
2. Check console for errors
3. Run: `./css` again

**Still not working?**
Full reset (takes 19s but guaranteed):
```bash
./update-static.sh
```

## Speed Comparison

- `./css` - 18 seconds ✅ **USE THIS - FOOLPROOF**
- `./update-static.sh` - 19 seconds (does same thing, longer name)

## Notes

- Only use `./css` - it's foolproof
- Django's ManifestStaticFilesStorage generates the hashed filenames
- Hashes change when file content changes
- Browser loads hashed version (e.g., `leaflet-measure.9ccf36ebeb9e.css`)
- Without collectstatic, browsers serve old hashed files forever
