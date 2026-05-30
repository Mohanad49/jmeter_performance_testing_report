@echo off
if not exist sample_results mkdir sample_results
if not exist reports mkdir reports

set JMETER_BIN=%JMETER_BIN%
if "%JMETER_BIN%"=="" set JMETER_BIN=jmeter

set THREADS=%THREADS%
if "%THREADS%"=="" set THREADS=50

set RAMP_UP=%RAMP_UP%
if "%RAMP_UP%"=="" set RAMP_UP=30

set DURATION=%DURATION%
if "%DURATION%"=="" set DURATION=120

set HOST=%HOST%
if "%HOST%"=="" set HOST=127.0.0.1

set PORT=%PORT%
if "%PORT%"=="" set PORT=8000

%JMETER_BIN% -n -t jmeter/car_price_prediction_load_test.jmx -Jhost=%HOST% -Jport=%PORT% -Jthreads=%THREADS% -Jramp_up=%RAMP_UP% -Jduration=%DURATION% -l sample_results/jmeter_results.jtl -e -o reports/html-dashboard
python scripts/generate_report.py --input sample_results/jmeter_results.jtl --output reports/performance_summary.md --scenario "%THREADS% users, %RAMP_UP%s ramp-up, %DURATION%s duration"
