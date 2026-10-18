# MEGA Sync Setup Guide for `CloudPII`

This guide outlines the manual steps to set up and verify real-time folder synchronization between your local PII directory (`E:\WORK\PROJECT\git\PersonalAssistant\CloudPII`) and your MEGA cloud storage using **MEGAcmd**.

> **Note on Security:** We do not perform local gzip compression or local file encryption because **MEGA natively applies client-side zero-knowledge encryption** (AES-128/256) on your device *before* uploading files to the cloud.

---

## **Prerequisites**
1. Ensure **MEGAcmd** is installed on your Windows machine.
2. Ensure your local folder exists: `E:\WORK\PROJECT\git\PersonalAssistant\CloudPII`

---

## **Step-by-Step Instructions**

### **1. Open MEGAcmd Shell**
Open the interactive command-line interface for MEGA:
- Search for **MEGAcmd Shell** in your Windows Start Menu and launch it.

### **2. Log into Your MEGA Account**
If you are not already logged in, enter your credentials:
```bash
login your_email@example.com
```
*(Enter your password when prompted).*

To verify you are logged in, check your status:
```bash
whoami
```

### **3. Create the Remote Cloud Directory**
Before syncing, ensure the target folder exists on your MEGA cloud:
```bash
mkdir /CloudPII
```

### **4. Initiate Folder Synchronization**
Run the `sync` command to link your local PII repository to your remote MEGA folder:
```bash
sync E:\WORK\PROJECT\git\PersonalAssistant\CloudPII /CloudPII
```

### **5. Verify Sync Status**
Check that the synchronization task is active and successfully synced:
```bash
sync
```
You should see output similar to:
```text
ID          LOCALPATH                                      REMOTEPATH RUN_STATE STATUS ERROR SIZE    FILES DIRS
xd9onvFLB6Y E:\WORK\PROJECT\git\PersonalAssistant\CloudPII /CloudPII  Running   Synced NO    2.21 KB 2     3
```

---

## **Background Behavior**
Once the `sync` command is active, MEGAcmd runs as a background Windows service (`MEGAcmdServer`). Any files added, modified, or deleted inside `E:\WORK\PROJECT\git\PersonalAssistant\CloudPII` will automatically and continuously sync in real time to `/CloudPII` on MEGA.
