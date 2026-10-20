# Guide: Sending PowerShell Commands to Another Machine on the Same Wi-Fi

To execute PowerShell commands on another machine connected to the same Wi-Fi network, you can use **PowerShell Remoting (WinRM)** or **SSH**, provided you have administrative credentials on the target machine and it has been configured to accept remote connections.

---

## Method 1: PowerShell Remoting (WinRM) — *Recommended for Windows-to-Windows*

This is the native, built-in way to manage Windows systems remotely via PowerShell.

### Step 1: Prepare the Target Machine (Run on the Target PC)
Before you can connect *to* the target machine, you must enable and configure PowerShell Remoting on it. 
1. Open PowerShell **as Administrator** on the target computer.
2. Run this command:
   ```powershell
   Enable-PSRemoting -Force
   ```
3. If both computers are on a private Wi-Fi network (which Windows often classifies as a public network by default), you may need to configure TrustedHosts. To allow connections from any machine on the local network, run:
   ```powershell
   Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force
   ```
   *(Note: For better security, replace `"*"` with the specific IP address or computer name of your machine).*

### Step 2: Connect from Your Machine (Run on Your PC)
Once configured, you can start an interactive session or run remote commands from your PowerShell console.

* **Interactive Session (like an SSH session):**
  ```powershell
  Enter-PSSession -ComputerName <Target_IP_Address_or_HostName> -Credential "<Target_Username>"
  ```
  *When prompted, enter the Windows password for the user account on the target machine. Once connected, your prompt will change to show the remote computer name. To exit, type `Exit-PSSession`.*

* **Run a Single Command Remotely:**
  ```powershell
  Invoke-Command -ComputerName <Target_IP_Address_or_HostName> -ScriptBlock { Get-Process } -Credential "<Target_Username>"
  ```

---

## Method 2: PowerShell via OpenSSH — *Alternative*

If the target machine has an OpenSSH Server installed:

1. **Enable OpenSSH Server on Target (Run as Admin):**
   ```powershell
   Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
   Start-Service sshd
   Set-Service -Name sshd -StartupType Automatic
   ```

2. **Connect from Your Machine:**
   ```powershell
   ssh <Target_Username>@<Target_IP_Address>
   ```
   Once logged in, type `powershell` to drop into a PowerShell prompt.

---

## ⚠️ Important Troubleshooting Checklist

1. **Find the Target IP Address:**
   On the target machine, run `ipconfig` to find its local IPv4 address (e.g., `192.168.1.15`).
2. **Firewall / Network Profile:** 
   Ensure your Wi-Fi network profile is set to **Private** so Windows Firewall allows local device communication:
   ```powershell
   Set-NetConnectionProfile -InterfaceIndex <Index> -NetworkCategory Private
   ```
