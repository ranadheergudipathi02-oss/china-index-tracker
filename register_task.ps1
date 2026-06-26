# Register a Windows Task Scheduler job for daily China index fetch.
# A-share market closes 15:00 CST (UTC+8) = 12:30 IST; run at 13:00 IST (15:30 CST).
# Run this script once as Administrator.

$taskName = "ChinaIndexTracker_Daily"
$batPath  = Join-Path $PSScriptRoot "run_daily.bat"

$action  = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory $PSScriptRoot
$trigger = New-ScheduledTaskTrigger -Daily -At "13:00"
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd `
    -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger `
    -Settings $settings -Description "Daily China A-share index constituent fetch (13:00 IST)"

Write-Host "Registered task '$taskName' for daily 13:00."
Write-Host "To test now:  Start-ScheduledTask -TaskName '$taskName'"
