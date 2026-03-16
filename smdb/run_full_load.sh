#!/bin/bash
# Full SMDB data load with hang detection, auto-restart, and guaranteed
# spreadsheets_load() as a final step regardless of interruptions.
# Run inside a screen session: screen -dmS full_load /home/docker_user/run_full_load.sh

DB_URL="postgres://VfWWmNjOAZnLwrPXRCfqpTQEzfSGKKBV:LMBp8yaATEKbyuv62lsEoAYxLxKoOnMXWSHBSKvT5jVHDmbnuSSwVlcIEYjruevC@postgres:5432/default"
CONTAINER="smdb-django-1"
LOG="/home/docker_user/mission_load.log"
STALL_LOG="/home/docker_user/mission_load_stall.log"
SPREADSHEET_LOG="/home/docker_user/spreadsheet_load.log"
STALL_MINUTES=15
MAX_RESTARTS=10

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$STALL_LOG"; }

# Step 1: Main load with hang detection and auto-restart
log "Starting main load (bootstrap + notes + fnv + compilation)"
restart_count=0

while true; do
    log "Load attempt $((restart_count+1)) of $MAX_RESTARTS..."

    docker exec -e DATABASE_URL="$DB_URL" "$CONTAINER" \
        bash -c "cd /app && python manage.py runscript load >> $LOG 2>&1" &
    LOAD_PID=$!

    last_size=0
    stall_seconds=0

    while kill -0 $LOAD_PID 2>/dev/null; do
        sleep 60
        cur_size=$(wc -c < "$LOG" 2>/dev/null || echo 0)
        if [ "$cur_size" -eq "$last_size" ]; then
            stall_seconds=$((stall_seconds + 60))
            log "No log progress for ${stall_seconds}s (threshold: $((STALL_MINUTES*60))s)"
            if [ "$stall_seconds" -ge "$((STALL_MINUTES * 60))" ]; then
                log "STALL DETECTED - killing load process (PID $LOAD_PID)"
                kill $LOAD_PID 2>/dev/null
                docker exec "$CONTAINER" bash -c "pkill -f 'manage.py runscript load'" 2>/dev/null
                break
            fi
        else
            stall_seconds=0
            last_size=$cur_size
        fi
    done

    wait $LOAD_PID
    EXIT_CODE=$?

    if [ $EXIT_CODE -eq 0 ]; then
        log "Main load completed successfully (exit code 0)"
        break
    else
        restart_count=$((restart_count + 1))
        log "Load exited with code $EXIT_CODE. Restart $restart_count of $MAX_RESTARTS"
        if [ $restart_count -ge $MAX_RESTARTS ]; then
            log "Max restarts reached. Proceeding to spreadsheets step anyway."
            break
        fi
        sleep 10
    fi
done

# Step 2: ALWAYS run spreadsheets_load() regardless of above outcome
log "Running spreadsheets_load() - guaranteed final step"
docker exec -e DATABASE_URL="$DB_URL" "$CONTAINER" \
    bash -c "cd /app && python run_spreadsheets.py" >> "$SPREADSHEET_LOG" 2>&1
SPREADSHEET_EXIT=$?
log "spreadsheets_load() finished with exit code $SPREADSHEET_EXIT"

# Step 3: Deduplication
log "Running deduplication"
docker exec -e DATABASE_URL="$DB_URL" "$CONTAINER" \
    bash -c "cd /app && python dedup_missions.py" | tee -a "$STALL_LOG"

# Step 4: Database backup
log "Running database backup"
BACKUP_FILE="/home/docker_user/smdb_backup_$(date +%Y%m%d_%H%M%S).sql.gz"
docker exec smdb-postgres-1 \
    bash -c "pg_dump -U VfWWmNjOAZnLwrPXRCfqpTQEzfSGKKBV default | gzip" > "$BACKUP_FILE"
log "Backup saved to $BACKUP_FILE ($(du -h "$BACKUP_FILE" | cut -f1))"

log "All steps complete"
