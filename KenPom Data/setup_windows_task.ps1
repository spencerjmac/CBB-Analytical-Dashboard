# PowerShell script to set up Windows Task Scheduler for daily KenPom scraping
# Run this as Administrator: Right-click PowerShell -> "Run as Administrator"

$taskName = "KenPom Daily Scrape"
$scriptPath = "C:\Users\spenc\OneDrive\Workspace\Tableau Final Project\run_daily_scrape.bat"
$workingDir = "C:\Users\spenc\OneDrive\Workspace\Tableau Final Project"

# Check if task already exists
$existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($existingTask) {
    Write-Host "Task '$taskName' already exists. Updating..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}

# Create the action (what to run)
$action = New-ScheduledTaskAction -Execute $scriptPath -WorkingDirectory $workingDir

# Create the trigger (daily at 2:00 AM)
$trigger = New-ScheduledTaskTrigger -Daily -At 2:00AM

# Create settings (run even if user is not logged on, restart on failure)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -RunOnlyIfNetworkAvailable

# Create the principal (run as current user)
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive -RunLevel Highest

# Register the task
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Daily KenPom data scrape and Tableau export"

Write-Host "`nTask '$taskName' has been created successfully!" -ForegroundColor Green
Write-Host "It will run daily at 2:00 AM" -ForegroundColor Green
Write-Host "`nTo verify, check Task Scheduler or run:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskName '$taskName'" -ForegroundColor Cyan
Write-Host "`nTo view task history:" -ForegroundColor Cyan
Write-Host "  Get-ScheduledTask -TaskName '$taskName' | Get-ScheduledTaskInfo" -ForegroundColor Cyan

