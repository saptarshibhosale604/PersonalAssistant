# Solution Plan: Recovering Raspberry Pi from Emergency Shell (`run-init: can't execute '/sbin/init'`)

This plan outlines the step-by-step procedure to diagnose and resolve the emergency shell boot failure caused by severe filesystem corruption and subsequent `fsck` cleanup on the Raspberry Pi root partition (`mmcblk0p2`, partition 2 on Disk 2).

---

## Phase 1: Preparation & Safety Check (Windows Host)
1. **Safely Access the SD Card:**
   - Drive `F:\` is the boot partition (`bootfs`, FAT32). Partition 2 (`mmcblk0p2`, `ext4`) is the Linux root filesystem, which is not natively readable on Windows without third-party drivers (like WSL2 or WSL mounted disk).
2. **Determine Access Method:**
   - **Recommended:** Connect the SD card to a Linux system, or use **WSL2** (Windows Subsystem for Linux) in Windows 11 to mount and inspect the ext4 root partition directly.

---

## Phase 2: Inspection & Diagnosis (via WSL2 / Linux Environment)
1. **Identify Device in Linux:**
   - Open PowerShell or WSL and locate the SD card device node (e.g., `/dev/sdb` or via `wsl --mount` / physical reader passthrough).
2. **Mount the Root Partition:**
   - Mount the ext4 root partition (`mmcblk0p2`) to a temporary directory (e.g., `/mnt/rootfs`).
3. **Inspect `/lost+found`:**
   - Check `/mnt/rootfs/lost+found/` to see if systemd (`/lib/systemd/systemd`), critical shared libraries (`libc.so.6`), or essential binaries were moved here during the `fsck` repair process.
4. **Verify `/sbin/init` and Target Integrity:**
   - Check the symbolic link `/mnt/rootfs/sbin/init`.
   - Verify if `../lib/systemd/systemd` exists and is a valid executable.

---

## Phase 3: Repair & Recovery Options

Depending on the findings in Phase 2, choose one of the following recovery paths:

### Option A: Restore from `/lost+found` (If files were recovered there)
1. Identify systemd and core binaries in `/lost+found/`.
2. Move them back to their original absolute paths (e.g., `/lib/systemd/systemd`).
3. Recreate or fix broken symbolic links if necessary.

### Option B: Reinstall / Re-populate Corrupted Packages (Using `apt` / `chroot`)
If systemd or essential libraries (`libc6`, `dpkg`, etc.) were completely destroyed/deleted by `fsck`:
1. **Chroot into the Root Partition:**
   ```bash
   mount --bind /dev /mnt/rootfs/dev
   mount --bind /proc /mnt/rootfs/proc
   mount --bind /sys /mnt/rootfs/sys
   chroot /mnt/rootfs
   ```
2. **Reinstall Essential Packages:**
   ```bash
   apt-get update
   apt-get install --reinstall systemd sysvinit-core libc6 udev base-files
   ```
3. Exit chroot, unmount cleanly, and sync disks.

### Option C: Overlay / Selective File Copy from a Working Image
If package management inside chroot fails due to database corruption:
1. Extract a fresh Raspberry Pi OS image (`.img`) of the same release date (`2026-09-15`).
2. Mount the root partition of the fresh image.
3. Copy missing system binaries (`/lib/systemd/systemd`, `/bin/sh`, `/sbin/init`, etc.) over to the corrupted root partition while preserving file permissions and ownership.

---

## Phase 4: Verification & Final Boot Test
1. **Run Filesystem Check Explicitly:**
   - Run `e2fsck -f /dev/sdX2` from Linux to ensure the ext4 filesystem is fully consistent and clean.
2. **Unmount Safely:**
   - Unmount all partitions (`umount /mnt/rootfs/...`).
3. **Hardware Test:**
   - Safely eject the SD card from the Windows/Linux host, insert it back into the Raspberry Pi, and power it on.
   - Verify that the system successfully passes the init stage and reaches login or systemd multi-user target.
