@echo off
echo Setting up Git and pushing to your GitHub repository...
echo.

REM Configure Git identity
git config --global user.name "Ayaan-A-Siddiqui"
git config --global user.email "ayaan@example.com"

REM Check if repository is already initialized
if not exist ".git" (
    echo Initializing Git repository...
    git init
)

REM Add all files
echo Adding all files to Git...
git add .

REM Create initial commit
echo Creating initial commit...
git commit -m "Initial commit: SEP QP Pack Generator with real data integration and configurable programs"

REM Add your GitHub repository as remote origin
echo Adding GitHub remote origin...
git remote add origin https://github.com/Ayaan-A-Siddiqui/MyProperty.git

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

if errorlevel 1 (
    echo Trying to push to master branch...
    git push -u origin master
)

echo.
echo ✅ Successfully pushed to your GitHub repository!
echo Visit: https://github.com/Ayaan-A-Siddiqui/MyProperty
echo.
pause 