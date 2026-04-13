# Issue #301 — Citation Sidebar Filter: Implementation Plan

## Goal
Make the `citation` (checkbox dropdown) and `citation_search` (text input) filter fields
visible and functional in the sidebar panel on the **Home** and **Missions** pages.

## Current State
Both fields are fully implemented in the backend and included in the sidebar form helper:
- `filters.py` — `citation` (ModelMultipleChoiceFilter) + `citation_search` (CharFilter)
- `forms.py` — both in `MissionFilterSidebarHelper` and `MissionFilterFormHelper`
- JS `filterKeys` arrays — both present across all pages

The gap is purely in the **sidebar UI rendering**:
- `citation` renders as a standard `<select multiple>`, not as `.form-check` checkboxes,
  so `setupCheckboxDropdowns()` skips it and it appears as an unstyled multi-select.
- `citation_search` text input may not be visually distinct enough in the sidebar.

## Step-by-Step Implementation

### Step 1 — `filters.py`: switch `citation` widget to `CheckboxSelectMultiple`
```python
from django.forms import CheckboxSelectMultiple

citation = ModelMultipleChoiceFilter(
    field_name="citations",
    queryset=Citation.objects.all().order_by("doi"),
    widget=CheckboxSelectMultiple,
)
```
This makes Django render each citation as a `.form-check` checkbox, allowing
`setupCheckboxDropdowns()` in `project.js` to pick it up automatically.

### Step 2 — Verify `setupCheckboxDropdowns` handles citation correctly
The function in `project.js` looks for `[id^="div_id_"]` wrappers containing `.form-check`
elements. With `CheckboxSelectMultiple`, the `div_id_citation` wrapper will contain
`.form-check` items — no JS changes should be needed.

Check that the label text reads "Citation" (from the filter's `label=` kwarg if set,
otherwise from the model field verbose name). Add `label="Citation"` in `filters.py`
if the auto-generated label is not clean.

### Step 3 — Verify `citation_search` styling in sidebar
The text input for `citation_search` has a placeholder
`"Citation (DOI or reference) contains..."`. Confirm it:
- Renders inside a `div_id_citation_search` wrapper
- Picks up the sidebar dark-theme text input styles from `map.css` /
  `map_mission_filter.css`
- Is not hidden or collapsed by any JS logic

### Step 4 — Home page (`map.js`) verification
The Home page sidebar builds its form by cloning the hidden crispy form. Confirm:
- `citation` and `citation_search` appear in the cloned sidebar form
- `setupCheckboxDropdowns()` is called on the cloned form after injection
- Both URL params (`citation`, `citation_search`) round-trip correctly through the
  existing `filterKeys` arrays (they are already listed)

### Step 5 — Clear button behavior
Both `citation` and `citation_search` are already in the JS `filterKeys` arrays used
by the Clear button logic — no extra changes needed. Verify by manual test.

### Step 6 — Tests
Run all 150 pytest tests:
```bash
docker exec django bash -c "cd /app/smdb && DJANGO_SETTINGS_MODULE=config.settings.test pytest -v"
```

## Files Likely Changed
| File | Change |
|------|--------|
| `smdb/smdb/filters.py` | Add `widget=CheckboxSelectMultiple` to `citation` filter |
| `smdb/smdb/static/js/project.js` | Possibly adjust `setupCheckboxDropdowns` if needed |
| `smdb/smdb/static/js/map.js` | Verify Home page sidebar clones citation correctly |
| `smdb/smdb/static/js/map_mission_filter.js` | Verify Missions page sidebar |

## Do NOT Change
- Missions page layout, Leaflet CSS/JS includes, or Clear-button logic
  (see `copilot-review-missions.mdc`)
- The `citation_search` CharFilter logic in `filters.py` (already correct)
- Any existing URL param handling (citation already in filterKeys)
