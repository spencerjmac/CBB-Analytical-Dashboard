# Script to permanently add UV to your system PATH
# Run this as Administrator: Right-click PowerShell -> "Run as Administrator"

$uvPath = "C:\Users\spenc\.local\bin"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")

if ($currentPath -notlike "*$uvPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$uvPath", "User")
    Write-Host "UV has been added to your user PATH!" -ForegroundColor Green
    Write-Host "Please restart your terminal for changes to take effect." -ForegroundColor Yellow
} else {
    Write-Host "UV is already in your PATH!" -ForegroundColor Green
}



