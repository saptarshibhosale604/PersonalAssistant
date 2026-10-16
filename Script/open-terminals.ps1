# PowerShell script to open 3 tabs in the same Windows Terminal window

$configPath = "E:\WORK\PROJECT\DotfilesWindows\Dotfiles00\Powershell\config.ps1"

$script1 = ". '$configPath'; cdPersonalAssistant; PersonalAssistant"
$script2 = ". '$configPath'; cdPersonalAssistant"

$encoded1 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script1))
$encoded2 = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($script2))

# Open first tab, then spawn 2 new tabs in the existing window using -w 0
wt -d . powershell -NoExit -EncodedCommand $encoded1
Start-Sleep -Milliseconds 300
wt -w 0 nt -d . powershell -NoExit -EncodedCommand $encoded2
wt -w 0 nt -d . powershell -NoExit -EncodedCommand $encoded2
