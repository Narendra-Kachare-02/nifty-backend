@echo off

REM Set PostgreSQL credentials
SET DB_NAME=askexpert
SET DB_USER=askexpert
SET DB_HOST=localhost
SET DB_PORT=5432

REM Drop all tables in PostgreSQL database
echo Dropping all tables in PostgreSQL database: %DB_NAME%

psql -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -c "DROP SCHEMA public CASCADE;"
psql -h %DB_HOST% -U %DB_USER% -d %DB_NAME% -c "CREATE SCHEMA public;"

REM Run migrations to recreate tables
echo Running migrations...
python manage.py migrate

echo PostgreSQL database reset completed.
pause
