Write-Host "Installing required packages for SEP QP Pack Generator..." -ForegroundColor Green

# Try to find conda
$condaPaths = @(
    "$env:USERPROFILE\Anaconda3\Scripts\conda.exe",
    "$env:USERPROFILE\miniconda3\Scripts\conda.exe",
    "C:\Anaconda3\Scripts\conda.exe",
    "C:\miniconda3\Scripts\conda.exe"
)

$condaFound = $false
foreach ($path in $condaPaths) {
    if (Test-Path $path) {
        Write-Host "Found conda at: $path" -ForegroundColor Yellow
        $env:PATH = "$(Split-Path $path);$env:PATH"
        $condaFound = $true
        break
    }
}

if (-not $condaFound) {
    Write-Host "Conda not found in common locations" -ForegroundColor Red
    Write-Host "Please install Anaconda/Miniconda or activate your environment manually" -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

# Try to activate conda environment
try {
    Write-Host "Activating conda..." -ForegroundColor Yellow
    & conda activate base
    Write-Host "Conda activated successfully" -ForegroundColor Green
} catch {
    Write-Host "Could not activate conda automatically" -ForegroundColor Yellow
    Write-Host "Please activate manually: conda activate [environment_name]" -ForegroundColor Yellow
}

# Install packages
Write-Host "Installing packages..." -ForegroundColor Yellow
& conda install -c conda-forge pandas geopandas numpy rasterio shapely reportlab tqdm fiona pyproj -y

Write-Host ""
Write-Host "Installation complete!" -ForegroundColor Green
Write-Host "You can now run: python qpland.py" -ForegroundColor Green
Read-Host "Press Enter to continue" 