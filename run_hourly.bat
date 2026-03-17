@echo off
:: ─────────────────────────────────────────────────────────────────────────────
:: run_hourly.bat  —  Bloomberg data pull + git push
:: Schedule this in Windows Task Scheduler to run every hour.
:: Requires: Bloomberg Terminal open, Python (Anaconda), Git installed.
:: ─────────────────────────────────────────────────────────────────────────────

set DASHBOARD_DIR=C:\Users\scott\OneDrive\Documents\Research\Claude Dashboard
set LOG_FILE=%DASHBOARD_DIR%\pull.log

echo [%DATE% %TIME%] Starting data pull... >> "%LOG_FILE%"

:: Activate Anaconda base environment and run the pull script
call C:\Users\scott\Anaconda3\Scripts\activate.bat base
cd /d "%DASHBOARD_DIR%"
python bloomberg_pull.py >> "%LOG_FILE%" 2>&1

echo [%DATE% %TIME%] Pull complete. >> "%LOG_FILE%"
