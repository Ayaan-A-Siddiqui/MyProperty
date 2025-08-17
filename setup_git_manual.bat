@echo off
echo Setting up Git repository for SEP QP Pack Generator...
echo.

REM Try to find Git in common locations
set GIT_PATH=

if exist "C:\Program Files\Git\bin\git.exe" (
    set GIT_PATH="C:\Program Files\Git\bin\git.exe"
    echo Found Git at: C:\Program Files\Git\bin\git.exe
) else if exist "C:\Program Files (x86)\Git\bin\git.exe" (
    set GIT_PATH="C:\Program Files (x86)\Git\bin\git.exe"
    echo Found Git at: C:\Program Files (x86)\Git\bin\git.exe
) else if exist "%USERPROFILE%\AppData\Local\Programs\Git\bin\git.exe" (
    set GIT_PATH="%USERPROFILE%\AppData\Local\Programs\Git\bin\git.exe"
    echo Found Git at: %USERPROFILE%\AppData\Local\Programs\Git\bin\git.exe
) else (
    echo Git not found in common locations.
    echo Please install Git from: https://git-scm.com/downloads
    echo After installation, run this script again.
    pause
    exit /b 1
)

echo.
echo Initializing Git repository...

REM Initialize Git repository
%GIT_PATH% init
if errorlevel 1 (
    echo Failed to initialize Git repository
    pause
    exit /b 1
)

REM Add all files
echo Adding files to Git...
%GIT_PATH% add .
if errorlevel 1 (
    echo Failed to add files to Git
    pause
    exit /b 1
)

REM Create initial commit
echo Creating initial commit...
%GIT_PATH% commit -m "Initial commit: SEP QP Pack Generator with real data integration"
if errorlevel 1 (
    echo Failed to create initial commit
    pause
    exit /b 1
)

echo.
echo Git repository setup complete!
echo.
echo Next steps:
echo 1. Create a new repository on GitHub
echo 2. Add the remote origin:
echo    %GIT_PATH% remote add origin https://github.com/YOUR_USERNAME/sep-qp-generator.git
echo 3. Push to GitHub:
echo    %GIT_PATH% push -u origin main
echo.
echo Your repository is ready for GitHub!
pause 