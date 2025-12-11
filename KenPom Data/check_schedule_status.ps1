# Script to check if the scheduled task is set up and running correctly

$taskName = "KenPom Daily Scrape"

Write-Host "Checking scheduled task status..." -ForegroundColor Cyan
Write-Host ""

try {
    $task = Get-ScheduledTask -TaskName $taskName -ErrorAction Stop
    
    Write-Host "Task Name: $($task.TaskName)" -ForegroundColor Green
    Write-Host "State: $($task.State)" -ForegroundColor $(if ($task.State -eq 'Ready') { 'Green' } else { 'Yellow' })
    
    $taskInfo = Get-ScheduledTaskInfo -TaskName $taskName
    Write-Host "Last Run Time: $($taskInfo.LastRunTime)" -ForegroundColor Cyan
    Write-Host "Last Result: $($taskInfo.LastResult)" -ForegroundColor $(if ($taskInfo.LastResult -eq 0) { 'Green' } else { 'Red' })
    Write-Host "Next Run Time: $($taskInfo.NextRunTime)" -ForegroundColor Cyan
    
    # Check triggers
    Write-Host "`nTriggers:" -ForegroundColor Cyan
    foreach ($trigger in $task.Triggers) {
        Write-Host "  - $($trigger.CimClass.CimClassName): $($trigger.StartBoundary)" -ForegroundColor White
    }
    
    Write-Host "`nTask is configured correctly!" -ForegroundColor Green
    
} catch {
    Write-Host "ERROR: Task '$taskName' not found!" -ForegroundColor Red
    Write-Host "`nTo set it up, run:" -ForegroundColor Yellow
    Write-Host "  .\setup_windows_task.ps1" -ForegroundColor Yellow
    Write-Host "`n(As Administrator)" -ForegroundColor Yellow
}

Write-Host "`nRecent log entries:" -ForegroundColor Cyan
if (Test-Path "scrape_log.txt") {
    Get-Content scrape_log.txt -Tail 10
} else {
    Write-Host "  No log file found yet" -ForegroundColor Yellow
}

Write-Host "`nCSV file status:" -ForegroundColor Cyan
if (Test-Path "kenpom_tableau.csv") {
    $csvInfo = Get-Item "kenpom_tableau.csv"
    Write-Host "  File exists: Yes" -ForegroundColor Green
    Write-Host "  Last modified: $($csvInfo.LastWriteTime)" -ForegroundColor White
    Write-Host "  Size: $([math]::Round($csvInfo.Length / 1KB, 2)) KB" -ForegroundColor White
} else {
    Write-Host "  File not found" -ForegroundColor Red
}

