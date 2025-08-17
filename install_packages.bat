@echo off
echo Installing required packages for SEP QP Pack Generator...

REM Try to find and activate conda
if exist "%USERPROFILE%\Anaconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\Anaconda3\Scripts\activate.bat"
    echo Anaconda activated
) else if exist "%USERPROFILE%\miniconda3\Scripts\activate.bat" (
    call "%USERPROFILE%\miniconda3\Scripts\activate.bat"
    echo Miniconda activated
) else if exist "C:\Anaconda3\Scripts\activate.bat" (
    call "C:\Anaconda3\Scripts\activate.bat"
    echo Anaconda activated
) else if exist "C:\miniconda3\Scripts\activate.bat" (
    call "C:\miniconda3\Scripts\activate.bat"
    echo Miniconda activated
) else (
    echo Conda not found in common locations
    echo Please activate your conda environment manually
    pause
    exit /b 1
)

REM Install packages
echo Installing packages...
conda install -c conda-forge pandas geopandas numpy rasterio shapely reportlab tqdm fiona pyproj -y

echo.
echo Installation complete!
echo You can now run: python qpland.py
pause 