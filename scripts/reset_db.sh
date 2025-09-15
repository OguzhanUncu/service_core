#!/bin/bash

DB_NAME="service_core"
DB_USER="postgres"
DB_PASSWORD="q"
DB_HOST="localhost"
DB_PORT="5432"

export PGPASSWORD=$DB_PASSWORD

# close connections
psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d postgres -c "
    SELECT pg_terminate_backend(pid)
    FROM pg_stat_activity
    WHERE datname = '$DB_NAME' AND pid <> pg_backend_pid();
" > /dev/null

psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d postgres -c "DROP DATABASE IF EXISTS $DB_NAME;" > /dev/null

psql -U "$DB_USER" -h "$DB_HOST" -p "$DB_PORT" -d postgres -c "CREATE DATABASE $DB_NAME WITH OWNER = $DB_USER;" > /dev/null

echo "Database '$DB_NAME' reset complete"
