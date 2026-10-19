@echo off
echo ======================================================================
echo    Starting QKraft: Spring Boot + JavaScript/HTML/CSS + PostgreSQL
echo ======================================================================

cd /d "%~dp0springboot-backend"
echo [1/2] Connecting to PostgreSQL (5432/qkraft)...
echo [2/2] Launching Spring Boot server on port 8000...
echo.
echo Application will be live at: http://localhost:8000
echo.

mvn spring-boot:run
pause
