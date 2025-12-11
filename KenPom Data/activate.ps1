# PowerShell script to activate the UV virtual environment
# Usage: .\activate.ps1

# Add UV to PATH for this session (if not already there)
$uvPath = "C:\Users\spenc\.local\bin"
if ($env:Path -notlike "*$uvPath*") {
    $env:Path = "$uvPath;$env:Path"
}

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1

Write-Host "Virtual environment activated!" -ForegroundColor Green
Write-Host "Python: $(python --version)" -ForegroundColor Cyan

# Check if UV is available
try {
    $uvVersion = uv --version 2>&1
    Write-Host "UV: $uvVersion" -ForegroundColor Cyan
} catch {
    Write-Host "UV: Not found in PATH (this is okay if you don't need UV commands)" -ForegroundColor Yellow
    Write-Host "  To add UV permanently, add C:\Users\spenc\.local\bin to your system PATH" -ForegroundColor Yellow
}

