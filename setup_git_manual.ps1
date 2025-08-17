Write-Host "Setting up Git repository for SEP QP Pack Generator..." -ForegroundColor Green
Write-Host ""

# Try to find Git in common locations
$gitPath = $null

$possiblePaths = @(
    "C:\Program Files\Git\bin\git.exe",
    "C:\Program Files (x86)\Git\bin\git.exe",
    "$env:USERPROFILE\AppData\Local\Programs\Git\bin\git.exe"
)

foreach ($path in $possiblePaths) {
    if (Test-Path $path) {
        $gitPath = $path
        Write-Host "Found Git at: $path" -ForegroundColor Yellow
        break
    }
}

if (-not $gitPath) {
    Write-Host "Git not found in common locations." -ForegroundColor Red
    Write-Host "Please install Git from: https://git-scm.com/downloads" -ForegroundColor Red
    Write-Host "After installation, run this script again." -ForegroundColor Red
    Read-Host "Press Enter to continue"
    exit 1
}

Write-Host ""
Write-Host "Initializing Git repository..." -ForegroundColor Yellow

try {
    # Initialize Git repository
    & $gitPath init
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to initialize Git repository"
    }
    Write-Host "✅ Git repository initialized" -ForegroundColor Green
    
    # Add all files
    Write-Host "Adding files to Git..." -ForegroundColor Yellow
    & $gitPath add .
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to add files to Git"
    }
    Write-Host "✅ Files added to Git" -ForegroundColor Green
    
    # Create initial commit
    Write-Host "Creating initial commit..." -ForegroundColor Yellow
    & $gitPath commit -m "Initial commit: SEP QP Pack Generator with real data integration"
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create initial commit"
    }
    Write-Host "✅ Initial commit created" -ForegroundColor Green
    
    Write-Host ""
    Write-Host "🎉 Git repository setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Create a new repository on GitHub" -ForegroundColor White
    Write-Host "2. Add the remote origin:" -ForegroundColor White
    Write-Host "   & $gitPath remote add origin https://github.com/YOUR_USERNAME/sep-qp-generator.git" -ForegroundColor Gray
    Write-Host "3. Push to GitHub:" -ForegroundColor White
    Write-Host "   & $gitPath push -u origin main" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Your repository is ready for GitHub!" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Git setup failed. Please check the error and try again." -ForegroundColor Red
}

Read-Host "Press Enter to continue" 