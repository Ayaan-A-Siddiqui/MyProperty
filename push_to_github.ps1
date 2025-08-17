Write-Host "🚀 Setting up Git and pushing to your GitHub repository..." -ForegroundColor Green
Write-Host ""

try {
    # Configure Git identity
    Write-Host "Configuring Git identity..." -ForegroundColor Yellow
    git config --global user.name "Ayaan-A-Siddiqui"
    git config --global user.email "ayaan@example.com"
    Write-Host "✅ Git identity configured" -ForegroundColor Green
    
    # Check if repository is already initialized
    if (-not (Test-Path ".git")) {
        Write-Host "Initializing Git repository..." -ForegroundColor Yellow
        git init
        Write-Host "✅ Git repository initialized" -ForegroundColor Green
    }
    
    # Add all files
    Write-Host "Adding all files to Git..." -ForegroundColor Yellow
    git add .
    Write-Host "✅ Files added to Git" -ForegroundColor Green
    
    # Create initial commit
    Write-Host "Creating initial commit..." -ForegroundColor Yellow
    git commit -m "Initial commit: SEP QP Pack Generator with real data integration and configurable programs"
    Write-Host "✅ Initial commit created" -ForegroundColor Green
    
    # Add your GitHub repository as remote origin
    Write-Host "Adding GitHub remote origin..." -ForegroundColor Yellow
    git remote add origin https://github.com/Ayaan-A-Siddiqui/MyProperty.git
    Write-Host "✅ GitHub remote added" -ForegroundColor Green
    
    # Push to GitHub
    Write-Host "Pushing to GitHub..." -ForegroundColor Yellow
    git push -u origin main
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Trying to push to master branch..." -ForegroundColor Yellow
        git push -u origin master
    }
    
    Write-Host ""
    Write-Host "🎉 Successfully pushed to your GitHub repository!" -ForegroundColor Green
    Write-Host "Visit: https://github.com/Ayaan-A-Siddiqui/MyProperty" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Git setup failed. Please check the error and try again." -ForegroundColor Red
}

Read-Host "Press Enter to continue" 