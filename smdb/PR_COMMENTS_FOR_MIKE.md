# PR Review Comments for Mike McCann

## Email to Mike: Response re test errors (pytest / Docker build)

**Copy the text below to reply to Mike's email about PR #286 test failures.**

---

Hi Mike,

I ran the same test and hit the same errors—so it wasn’t a merge issue on your side.

**What was going wrong**  
The failure was from the **Docker image build**, not from the test code. The Django image (GDAL base) uses Python 3.8, and several pins in `requirements/base.txt` (netCDF4, numpy, pandas, dask, xarray) don’t have wheels for Python 3.8, so the image failed to build and the test command never got to run.

**What we did**  
We’ve fixed this and **checked the fix into PR #286**. In `smdb/requirements/base.txt` we pinned those packages to versions that have Python 3.8 wheels and added a short comment so future dependency bumps don’t break the build again.

**What you should do**  
1. Pull the latest from the PR #286 branch (`review/filter-sidebar-improvements-consolidated`).
2. Run the test with an **explicit compose file** (e.g. from the `smdb` directory):
   ```bash
   docker compose -f local.yml run --rm django pytest smdb/smdb/tests/test_views.py -v
   ```
   Use whatever compose file you normally use for that environment (e.g. `production.yml` on the production server). **For the production server, see the step-by-step below.**
3. Make sure **PostgreSQL is running** before the test (e.g. `docker compose -f local.yml up -d` first).

The first run may build the image; after that the view tests should pass. If you still see a build or test error, send me the exact command and full output and we can track it down.

Thanks,  
Karen

---

## Step-by-step: Run view tests on production server (production.yml)

**For Mike (or anyone) on the production server (e.g. smdb.shore.mbari.org).**  
Use this when you are on the host where the app runs with `production.yml` and you want to run the view tests after merging PR #286.

**Assumptions:** You have shell access as the user that runs Docker (e.g. `docker_user`), the repo is at `/opt/SeafloorMappingDB`, and production env files exist at `smdb/.envs/.production/`.

---

### 1. Log in and go to the repo

```bash
# If you use a dedicated deploy user (as in README):
sudo -u docker_user -i

# Go to the repo root (adjust path if yours is different)
cd /opt/SeafloorMappingDB
```

---

### 2. Get the latest code with the fix

Pull the branch that has the dependency fix (and the rest of PR #286):

```bash
# Fetch and checkout the PR branch
git fetch origin review/filter-sidebar-improvements-consolidated
git checkout review/filter-sidebar-improvements-consolidated

# Or, if PR #286 is already merged into main:
# git checkout main
# git pull origin main
```

Confirm the fix is present (optional):

```bash
grep "netCDF4==1.7.2" smdb/requirements/base.txt
# Should print the line with netCDF4==1.7.2
```

---

### 3. Set environment variables

Same as for normal production runs (see README):

```bash
export DOCKER_USER_ID=$(id -u)
export SMDB_HOME=/opt/SeafloorMappingDB
export COMPOSE_FILE=$SMDB_HOME/smdb/production.yml
```

---

### 4. Ensure the stack is up (so Postgres and Redis are available)

The test runs in a one-off Django container that talks to the same Postgres (and Redis) as the app. Bring the stack up if it isn’t already:

```bash
docker compose up -d
```

Wait a few seconds for Postgres to be ready. Optionally check:

```bash
docker compose ps
# postgres and django (and redis, nginx, mb-system) should be up
```

---

### 5. Rebuild the Django image (so it uses the new pins)

The fix is in `requirements/base.txt`; production builds from `requirements/production.txt` (which includes `base.txt`). Rebuild the Django image once so the new pins are used:

```bash
docker compose build django
```

This can take several minutes. When it finishes, the image `smdb_production_django` will have the updated dependencies.

---

### 6. Run the view tests

From the **repo root** (`/opt/SeafloorMappingDB`), with `COMPOSE_FILE` set as above:

```bash
docker compose run --rm django pytest smdb/smdb/tests/test_views.py -v
```

Or from the **smdb** directory:

```bash
cd $SMDB_HOME/smdb
docker compose -f production.yml run --rm django pytest smdb/smdb/tests/test_views.py -v
```

- `run --rm` = one-off container, removed when the command exits.  
- The test needs `config.settings.test`; production compose uses production env files. The Django image still has `DJANGO_SETTINGS_MODULE` from the env file. For tests you may need the test settings. Check: if `.envs/.production/.django` (or the env passed to the container) sets `DJANGO_SETTINGS_MODULE=config.settings.test`, you’re good. If not, override for this run:

```bash
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test django pytest smdb/smdb/tests/test_views.py -v
```

---

### 7. Interpret the result

- **All tests passed** – You’re done. The fix and the test run are working.  
- **Build failed** – Share the full `docker compose build django` output (and, if different, the run command you used).  
- **Tests failed (e.g. DB or env)** – Share the full `docker compose run ... pytest ...` output.

---

### 8. (Optional) Switch back to your usual branch

If you had checked out the PR branch only to test:

```bash
git checkout main
# or your usual deploy branch
```

---

### Quick copy-paste (after PR #286 is on the server)

If the stack is already up and you only need to rebuild and run tests:

```bash
cd /opt/SeafloorMappingDB
export SMDB_HOME=/opt/SeafloorMappingDB
export COMPOSE_FILE=$SMDB_HOME/smdb/production.yml
export DOCKER_USER_ID=$(id -u)
docker compose build django
docker compose run --rm -e DJANGO_SETTINGS_MODULE=config.settings.test django pytest smdb/smdb/tests/test_views.py -v
```

(Adjust `SMDB_HOME` and paths if your server layout is different.)

---

## Comment 1: Reply to Mike's Comment on MissionTableView

**Use this when replying to Mike's comment about the paginated view issue:**

---

Thanks for catching this! I've fixed the issue in `MissionTableView` and also applied the same fix to `CompilationTableView` and `ExpeditionTableView` to prevent similar issues.

**Root Cause:**
The `MissionSerializer.to_representation()` method filters out missions without `nav_track` by returning `None` (lines 65-74). When missions were paginated first and then serialized, if all missions on a page lacked `nav_track`, they would all be filtered out during serialization, resulting in an empty map display.

**The Fix:**
I've added filtering at the database level **before pagination** in `MissionTableView` (commit `ba4b31a`):

```python
# Filter to only missions with nav_track before pagination (for map display)
# This ensures the map shows track lines, not just bounding boxes
# Missions without nav_track will be filtered out by the serializer anyway
missions = missions.filter(nav_track__isnull=False).exclude(nav_track__isempty=True)
```

This approach:
1. **Ensures consistency**: Only missions with `nav_track` are paginated, so they'll serialize correctly
2. **Matches existing pattern**: This is the same approach used in `MissionOverView.get_context_data()` (line 180)
3. **Prevents empty maps**: By filtering at the database level, we guarantee that paginated missions will have track data to display
4. **Maintains table/map sync**: The table and map now show the same missions (those with track data)

**Why this approach vs. Copilot's suggestion:**
Copilot's suggestion filtered before pagination but used the full queryset for map display. This fix filters before pagination and then paginates, ensuring the table and map show the same paginated set of missions, which provides a better user experience.

---

## Comment 2: Additional Fixes for Other Table Views

**Post as a new comment on the PR:**

---

I've also applied the same fix to `CompilationTableView` and `ExpeditionTableView` (commit `34ad0e7`) to prevent similar issues in those views.

**Why these views needed fixing:**
Both `CompilationTableView` and `ExpeditionTableView` use `MissionSerializer` to serialize missions for map display. Without filtering by `nav_track` at the database level, missions without track data would be filtered out during serialization, potentially leaving empty maps.

**Changes made:**
- **CompilationTableView** (line ~253): Added `nav_track` filtering before serialization
- **ExpeditionTableView** (line ~304): Added `nav_track` filtering before serialization

Both now filter missions to only those with `nav_track` before serialization:
```python
# Filter to only missions with nav_track (for map display)
# This ensures the map shows track lines, not just bounding boxes
missions = missions.filter(nav_track__isnull=False).exclude(nav_track__isempty=True)
```

This ensures consistency across all three table views (`MissionTableView`, `CompilationTableView`, `ExpeditionTableView`) and prevents empty map displays when missions matching the filters don't have `nav_track` data.

---

## Comment 3: Sidebar Filter and Clear Buttons Fix

**Post as a new comment on the PR:**

---

Fixed the Filter and Clear buttons in the sidebar that were missing after recent changes (commits `ea42994` and `5841a26`).

**Problem:**
After removing duplicate button creation code, the Filter and Clear buttons disappeared from the sidebar filter forms. The buttons needed to be restored with proper alignment and consistent styling.

**Solution:**
1. **Commented out Crispy Django buttons** in `forms.py`:
   - `MissionFilterSidebarHelper`: Commented out the `Div` containing `Submit` and `Reset` buttons
   - `ExpeditionFilterSidebarHelper`: Commented out the `Div` containing `Submit` and `Reset` buttons  
   - `CompilationFilterSidebarHelper`: Commented out the `Div` containing `Submit` and `Reset` buttons
   - Added comments indicating buttons are created dynamically by JavaScript

2. **Added JavaScript button creation** in `map.js`:
   - Creates Filter and Clear buttons dynamically with explicit matching styles
   - Both buttons have identical dimensions (38px height, 6px 12px padding, 0px margins)
   - Proper vertical alignment using flexbox (`align-items: center`)
   - Added `setTimeout` to re-apply styles after other JavaScript runs to override conflicting CSS

3. **Fixed conflicting CSS**:
   - Overrides `project.css` margin rules (`margin: 0.5em` → `margin: 0px`)
   - Overrides `filters.css` height rules (fixed height for `.btn-primary` but not `.btn-secondary`)
   - Ensures both buttons have matching borders, padding, and alignment

**Result:**
- Both buttons are now properly displayed, aligned vertically, and have consistent styling
- Buttons maintain proper form submission functionality
- Improved spacing: more space above buttons (1.5rem), less space below (0.25rem)

**Files Changed:**
- `smdb/forms.py`: Commented out Crispy button definitions in all three sidebar form helpers
- `smdb/static/js/map.js`: Added dynamic button creation with explicit styling and style re-application logic

**Commits:**
- `ea42994`: Fix: Restore Filter and Clear buttons in sidebar with proper alignment
- `5841a26`: docs: Add sidebar button fix comment for PR review
- `8342801`: Fix: Parse tmin/tmax date strings to prevent TypeError + add tests

---

## Comment 4: Fix TypeError with tmin/tmax Date Parameters

**Post as a new comment on the PR:**

---

Fixed the `TypeError: combine() argument 1 must be datetime.date, not SafeString` error that occurs when using `tmin`/`tmax` date filtering parameters (commit `8342801`).

**Problem:**
When `tmin` and `tmax` query parameters are passed to views, they come as strings (or SafeString objects from templates). The code was using these strings directly in Django ORM date field filters (`start_date__gte=min_date`), which internally calls `datetime.combine()`. This function expects a `date` object, not a SafeString, causing a TypeError.

**Solution:**
1. **Added date parsing** using Django's `parse_date()` utility:
   - `MissionOverView.get_context_data()`: Parse `tmin`/`tmax` strings to date objects before filtering
   - `MissionSelectAPIView.get()`: Parse `tmin`/`tmax` strings to date objects before filtering
   - `MissionExportAPIView.get()`: Parse `tmin`/`tmax` strings to date objects before filtering

2. **Added comprehensive tests** to prevent regressions:
   - Test valid date strings (YYYY-MM-DD format)
   - Test empty date strings
   - Test missing dates (only tmin or only tmax)
   - Test invalid date formats
   - Tests cover all three views that use date filtering

**Code Changes:**
```python
# Before (caused TypeError):
if context["view"].request.GET.get("tmin"):
    min_date = context["view"].request.GET.get("tmin")
    max_date = context["view"].request.GET.get("tmax")
    missions = missions.filter(
        start_date__gte=min_date,  # TypeError: SafeString passed to datetime.combine()
        end_date__lte=max_date,
    )

# After (fixed):
if context["view"].request.GET.get("tmin"):
    min_date_str = context["view"].request.GET.get("tmin")
    max_date_str = context["view"].request.GET.get("tmax")
    min_date = parse_date(str(min_date_str)) if min_date_str else None
    max_date = parse_date(str(max_date_str)) if max_date_str else None
    if min_date and max_date:
        missions = missions.filter(
            start_date__gte=min_date,  # Now a proper date object
            end_date__lte=max_date,
        )
```

**Why tests didn't catch this:**
The existing tests only checked that pages load (status 200) but didn't test date filtering functionality. No tests passed `tmin`/`tmax` parameters, so this code path was never executed. Added 8 new tests to cover date filtering scenarios.

**Files Changed:**
- `smdb/views.py`: Added `parse_date()` imports and date parsing logic in three views
- `smdb/tests/test_views.py`: Added 8 comprehensive tests for date filtering

---

## Comment 5: Running the view tests

**For Mike (and anyone merging/ testing PR #286):**

If the Docker image fails to build when you run the tests, it’s due to dependency pins in `requirements/base.txt` that don’t have wheels for Python 3.8 in the GDAL image. This PR includes version relaxations (netCDF4, numpy, pandas, dask, xarray) so the image builds.

**How to run the view tests**

1. **Use an explicit compose file** (from the repo root or from `smdb`):

   From repo root (`SeafloorMappingDB/`):
   ```bash
   export COMPOSE_FILE=$SMDB_HOME/smdb/local.yml
   docker-compose run --rm django pytest smdb/smdb/tests/test_views.py -v
   ```

   Or from the `smdb` directory:
   ```bash
   cd smdb
   docker compose -f local.yml run --rm django pytest smdb/smdb/tests/test_views.py -v
   ```

   On production or staging, use the same command with your compose file (e.g. `production.yml` or `production_localhost.yml`).

2. **Ensure PostgreSQL is running.** The django container’s entrypoint waits for Postgres. If you normally start the stack with `docker-compose up -d` (or `docker compose -f local.yml up -d`), do that first so postgres is up, then run the `docker-compose run ... pytest` command above.

3. **First run may need a build.** After pulling/merging, the first run may build the image (and apply the dependency fixes). Later runs will use the cached image.

---

## Summary

**All commits pushed to:** `review/filter-sidebar-improvements-consolidated` branch

**PR URL:** https://github.com/mbari-org/SeafloorMappingDB/pull/286

**Key Changes:**
1. Fixed mission display on map (nav_track filtering)
2. Fixed sidebar Filter/Clear buttons (alignment and styling)
