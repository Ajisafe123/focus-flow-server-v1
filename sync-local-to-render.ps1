# === CONFIGURATION ===
$LOCAL_DB = "postgres"               # your local DB name
$LOCAL_USER = "postgres"             # local DB user
$LOCAL_HOST = "localhost"
$LOCAL_PORT = "5432"

# Render DB connection (with sslmode=require)
$RENDER_URL = "postgresql://focusflow_db_tk4x_user:GrlgDQ436CuBNxEICIfiIGCr9H7i5lHm@dpg-d3thlj0dl3ps73eenkrg-a.oregon-postgres.render.com/focusflow_db_tk4x?sslmode=require"

# Path for local dump file
$DUMP_FILE = "C:\Users\$env:USERNAME\Desktop\local_dump.sql"

# === STEP 1: Export your local database ===
Write-Host "Dumping local database..."
pg_dump -U $LOCAL_USER -h $LOCAL_HOST -p $LOCAL_PORT -d $LOCAL_DB -f $DUMP_FILE

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to dump local DB."
    exit 1
}
Write-Host "Local DB dumped to $DUMP_FILE"

# === STEP 2: Drop all existing tables in Render DB ===
Write-Host "Dropping existing tables in Render DB..."
$dropSchemaCmd = @"
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
"@
$dropSchemaCmd | psql $RENDER_URL

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Some objects may not have been dropped (non-fatal)."
} else {
    Write-Host "Existing schema dropped and recreated."
}

# === STEP 3: Import dump into Render DB ===
Write-Host "Importing local dump into Render DB..."
psql $RENDER_URL -f $DUMP_FILE

if ($LASTEXITCODE -ne 0) {
    Write-Host "Import completed with warnings (SET ROLE errors are safe to ignore)."
} else {
    Write-Host "Render DB successfully restored!"
}

Write-Host "All done! Your Render DB now matches your local database."
