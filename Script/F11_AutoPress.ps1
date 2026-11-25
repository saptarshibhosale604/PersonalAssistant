# F11 Auto-Press Script - Runs every 4 minutes
# Press Ctrl+C to stop

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName PresentationCore

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  F11 AUTO-PRESS DAEMON INITIATED" -ForegroundColor Green
Write-Host "  Interval: 4 minutes (240 seconds)" -ForegroundColor Yellow
Write-Host "  Press Ctrl+C to terminate" -ForegroundColor Red
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$interval = 240  # 4 minutes in seconds
$counter = 0

try {
    while ($true) {
        Start-Sleep -Seconds $interval
        $counter++
        $timestamp = Get-Date -Format "HH:mm:ss"
        
        # Send F11 key
        [System.Windows.Forms.SendKeys]::SendWait("{F11}")
        
        # Log the action
        Write-Host "[$timestamp] Cycle #$counter - F11 SENT" -ForegroundColor Green
        Write-Host "  Next press in 4 minutes..." -ForegroundColor Gray
        Write-Host ""
    }
}
catch {
    Write-Host "`n[TERMINATED] F11 Auto-Press stopped by user" -ForegroundColor Red
}
finally {
    Write-Host "Session complete. Total cycles: $counter" -ForegroundColor Cyan
    Read-Host "Press Enter to close this window"
}