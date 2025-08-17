@echo off
echo Pushing to GitHub...
echo.

REM Set Git identity
git config --global user.name "Ayaan-A-Siddiqui"
git config --global user.email "ayaansiddiqu2022@gmail.com"

REM Add all files
git add .

REM Commit
git commit -m "Initial commit: SEP QP Pack Generator with real data integration and configurable programs"

REM Push to GitHub
echo.
echo Pushing to GitHub repository...
echo You may be prompted for your GitHub username and password/token
echo.
git push -u origin master

echo.
echo Done! Check your repository at: https://github.com/Ayaan-A-Siddiqui/MyProperty
pause 