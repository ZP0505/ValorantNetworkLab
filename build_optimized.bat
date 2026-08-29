@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==================================================
echo      Valorant Network Lab - Optimized Builder
echo ==================================================
echo.

python -m pip install -r requirements.txt
if errorlevel 1 goto :error

python -m pip install pyinstaller
if errorlevel 1 goto :error

echo.
echo Generating application icon...
python generate_icon.py
if errorlevel 1 goto :error

set "UPXDIR="

if exist "%~dp0tools\upx\upx.exe" (
    set "UPXDIR=%~dp0tools\upx"
    echo [OK] Found UPX: tools\upx\upx.exe
) else (
    where upx.exe >nul 2>nul
    if not errorlevel 1 (
        for %%I in (upx.exe) do set "UPXDIR=%%~dp$PATH:I"
        echo [OK] Found UPX in PATH.
    ) else (
        echo [WARNING] UPX not found.
        echo Build will continue without UPX compression.
        echo.
        echo To enable UPX:
        echo   Put upx.exe here:
        echo   tools\upx\upx.exe
        echo.
    )
)

echo.
echo Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo.
echo Building optimized EXE...
echo.

if defined UPXDIR (
    pyinstaller --noconfirm --clean --upx-dir "%UPXDIR%" "ValorantNetworkLab.spec"
) else (
    pyinstaller --noconfirm --clean "ValorantNetworkLab.spec"
)

if errorlevel 1 goto :error

echo.
echo ==================================================
echo Build successful!
echo ==================================================

for %%F in ("%~dp0dist\ValorantNetworkLab.exe") do (
    echo Output:
    echo %%~fF
    echo.
    echo Size:
    powershell -NoProfile -Command "$s=(Get-Item '%%~fF').Length; '{0:N2} MB' -f ($s/1MB)"
)

echo.
explorer "%~dp0dist"
pause
exit /b 0

:error
echo.
echo ==================================================
echo Build failed.
echo Copy the full error message to ChatGPT.
echo ==================================================
pause
exit /b 1
