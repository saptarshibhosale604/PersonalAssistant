# ==========================================
# PersonalAssistant Startup Script for WAHA & Bridge
# ==========================================

$ErrorActionPreference = "Stop"

$script:stepCounter = 0

function Run-Step([string]$Description, [scriptblock]$Action, [int]$WaitAfterSeconds = 0, [switch]$WaitForWahaWorking) {
    $script:stepCounter++
    $stepNum = "{0:D2}" -f $script:stepCounter
    
    Write-Host "`n----------------------------------------" -ForegroundColor Cyan
    Write-Host "STEP $stepNum`: $Description" -ForegroundColor Yellow
    Write-Host "Waiting for 3 seconds..." -ForegroundColor DarkGray
    Start-Sleep -Seconds 3
    
    Write-Host "Running command..." -ForegroundColor Green
    try {
        & $Action
        
        if ($WaitAfterSeconds -gt 0) {
            Write-Host "Waiting for $WaitAfterSeconds seconds for service/container initialization..." -ForegroundColor DarkGray
            Start-Sleep -Seconds $WaitAfterSeconds
        }
        
        if ($WaitForWahaWorking) {
            Write-Host "Waiting for WAHA session status to become 'WORKING'..." -ForegroundColor Yellow
            $maxAttempts = 40 # Up to 2 minutes (40 * 3s)
            $attempt = 0
            $isWorking = $false

            while ($attempt -lt $maxAttempts) {
                $attempt++
                try {
                    $statusResponse = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/session_01m4w6fcbnbvqc6j5be35bp1vb" `
                       -Headers @{ "x-api-key" = "0169fae66756404188915888e0827b7c" }
                    
                    if ($statusResponse.status -eq "WORKING") {
                        Write-Host "WAHA session status is WORKING!" -ForegroundColor Green
                        $statusResponse | Format-List
                        $isWorking = $true
                        break
                    } else {
                        Write-Host "Current session status: $($statusResponse.status). Waiting... (Attempt $attempt/$maxAttempts)" -ForegroundColor DarkGray
                    }
                }
                catch {
                    Write-Host "Connecting to session API... (Attempt $attempt/$maxAttempts)" -ForegroundColor DarkGray
                }
                Start-Sleep -Seconds 3
            }

            if (-not $isWorking) {
                throw "WAHA session did not reach 'WORKING' status within the expected time."
            }
        }
        
        Write-Host "[SUCCESS] Step completed." -ForegroundColor Green
    }
    catch {
        Write-Host "[ERROR/WARNING] $_" -ForegroundColor Red
    }
}

# 1. Start Docker Desktop and wait until it is running
Run-Step "Starting Docker Desktop & Waiting for Engine" {
    Write-Host "Command: Start-Process 'C:\Program Files\Docker\Docker\Docker Desktop.exe'"
    Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
    
    Write-Host "Checking Docker engine status..." -ForegroundColor Yellow
    $maxAttempts = 60 # wait up to 3 minutes (60 * 3s)
    $attempt = 0
    $dockerRunning = $false

    while ($attempt -lt $maxAttempts) {
        $attempt++
        try {
            $null = docker info 2>&1
            if ($LASTEXITCODE -eq 0) {
                $dockerRunning = $true
                break
            }
        } catch {
            # Docker not ready yet
        }
        Write-Host "Waiting for Docker daemon to start... (Attempt $attempt/$maxAttempts)" -ForegroundColor DarkGray
        Start-Sleep -Seconds 3
    }

    if (-not $dockerRunning) {
        throw "Docker Desktop failed to start within the expected time."
    }
    Write-Host "Docker Desktop is fully up and running!" -ForegroundColor Green
}

# 2. Start the WAHA container
Run-Step "Starting WAHA docker container" {
    Set-Location "E:\WORK\PROJECT\git\PersonalAssistant\UI\WhatsApp"
    $envPwd = (Get-Location).Path
    $cmd = "docker run -d -it --env-file `"$envPwd/.env`" -v `"$envPwd/sessions:/app/.sessions`" --rm -p 3000:3000 --name waha devlikeapro/waha"
    Write-Host "Command: $cmd"
    
    Start-Sleep -Seconds 2
    docker run -d -it --env-file "$envPwd/.env" -v "$envPwd/sessions:/app/.sessions" --rm -p 3000:3000 --name waha devlikeapro/waha
} -WaitAfterSeconds 20

# 3. Configure the webhook
Run-Step "Configuring WAHA session webhook" {
    Write-Host "Command: Invoke-RestMethod (PUT /api/sessions/session_01m4w6fcbnbvqc6j5be35bp1vb)"
    $body = @{
       config = @{
         webhooks = @(@{ url = "http://host.docker.internal:5002/webhook"; events = @("message.any") })
         ignore   = @{ status = $true; groups = $true; channels = $true; broadcast = $true }
       }
    }

    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/session_01m4w6fcbnbvqc6j5be35bp1vb" -Method PUT `
       -Headers @{ "x-api-key" = "0169fae66756404188915888e0827b7c" } -ContentType "application/json" -Body ($body | ConvertTo-Json -Depth 10)
       
    Write-Host "Webhook Configuration Result:" -ForegroundColor Cyan
    $response | Format-List
}

# 4. Check the webhook status and wait until status is WORKING
Run-Step "Checking WAHA session webhook status" {
    Write-Host "Command: Invoke-RestMethod (GET /api/sessions/session_01m4w6fcbnbvqc6j5be35bp1vb)"
    $response = Invoke-RestMethod -Uri "http://localhost:3000/api/sessions/session_01m4w6fcbnbvqc6j5be35bp1vb" `
       -Headers @{ "x-api-key" = "0169fae66756404188915888e0827b7c" }
       
    Write-Host "Initial Session Status Result:" -ForegroundColor Cyan
    $response | Format-List
} -WaitForWahaWorking

# 5. Start the waha bridge
Run-Step "Starting Python WAHA bridge" {
    Set-Location "E:\WORK\PROJECT\git\PersonalAssistant\"
    $cmd = "python -m UI.WhatsApp.waha_bridge"
    Write-Host "Command: $cmd"
    python -m UI.WhatsApp.waha_bridge
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "All startup steps executed!" -ForegroundColor Green
