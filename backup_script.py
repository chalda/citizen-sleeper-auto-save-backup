#!/usr/bin/env python3
"""
Periodic backup script for Citizen Sleeper save data.
Monitors a game save folder and creates timestamped backups when changes are detected.
The game periodically overwrites the savegame files as you play that can be corrupted in case of a crash.
Seemingly a common issue, with some players losing playthroughs dozens of hours into the game.
If you click Continue and get an infinite loading screen, bad savefile is probably the reason. 
The default paths for different OSes are defined but but your milage may vary.
Default save paths are defined but only tested on Windows, please report issues or alternative setups.
Dont save scum, let the dice fall where they do.
"""

"""
Features:
 - checks save file location based on your OS, known defaults are defined below and can be modified if needed
 - creates a copy of the entire gamedata folder
 - copies are appended a timestamp and stored in a 'backups' folder local to the script
 - checks if savefile has been modified since last copy to avoid filling your drive if you left the script running
 - backup frequency can be configured below, defaults to 10 minutes

Running:
No external deps, on most OSes should run with 
python ./backup_script.py
Windows users can now install python from the App Store and run the script with
py.exe .\backup_script.py
"""

import os
import sys
import shutil
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Backup frequency in seconds (default: 10 minutes)
BACKUP_FREQUENCY_SECONDS = 10 * 60

# Save files to monitor for changes
SAVE_FILE_NAMES = ["save_1.dat", "save_2.dat", "save_3.dat"]

# OS-specific folder paths
SAVE_PATHS = {
    "windows": Path("C:/Users") / os.getenv("USERNAME", "User") / "AppData/LocalLow/Jump Over the Age/Citizen Sleeper",
    "windows_app_store": Path("C:/Users") / os.getenv("USERNAME", "User") / "AppData/Local/Packages/SurpriseAttackPtyLtd.CitizenSleeper_8k24hnfn3vvj0/SystemAppData/wgs",
    "macos1": Path.home() / "Library/Application Support/Jump Over the Age/Citizen Sleeper",
    "macos2": Path.home() / "Library/Saved Application State/com.JumpOvertheAge.CitizenSleeper",
    "linux": Path.home() / ".local/share/Jump Over the Age/Citizen Sleeper",
    "steamos": Path.home() / ".local/share/steamapps/compatdata/1578650/pfx/",
}

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_system_paths() -> list[Path]:
    """
    Get the relevant save paths for the current operating system.
    
    Returns:
        List of Path objects to check for the save folder.
    """
    system = sys.platform
    
    if system == "win32":
        return [SAVE_PATHS["windows"], SAVE_PATHS["windows_app_store"]]
    elif system == "darwin":  # macOS
        return [SAVE_PATHS["macos1"], SAVE_PATHS["macos2"]]
    elif system == "linux":
        return [SAVE_PATHS["linux"], [SAVE_PATHS["steamos"]]]
    elif system == "linux2":  # Some Linux versions
        return [SAVE_PATHS["linux"]]
    else:
        # Fallback to all paths if system is unknown
        return list(SAVE_PATHS.values())


def find_save_folder() -> Optional[Path]:
    """
    Find the save folder by checking OS-specific paths.
    
    Returns:
        Path to the save folder if found, None otherwise.
    """
    paths_to_check = get_system_paths()
    
    for path in paths_to_check:
        if path.exists() and path.is_dir():
            print(f"✓ Found save folder: {path}")
            return path
    
    return None


def wait_for_save_folder(timeout: Optional[int] = None) -> Path:
    """
    Wait for the save folder to appear, checking periodically.
    
    Args:
        timeout: Maximum time to wait in seconds. None for indefinite.
    
    Returns:
        Path to the save folder once found.
    
    Raises:
        TimeoutError: If folder not found within timeout period.
    """
    start_time = time.time()
    
    print("Waiting for save folder to appear...")
    print(f"Checking paths every {BACKUP_FREQUENCY_SECONDS} seconds...")
    
    while True:
        save_folder = find_save_folder()
        
        if save_folder is not None:
            return save_folder
        
        if timeout is not None:
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(f"Save folder not found within {timeout} seconds")
        
        print(f"Save folder not found yet. Checking again in {BACKUP_FREQUENCY_SECONDS} seconds...")
        time.sleep(BACKUP_FREQUENCY_SECONDS)


def get_save_file_mtime(save_folder: Path, save_file_name: str) -> Optional[float]:
    """
    Get the last modified time of a specific save file.
    
    Args:
        save_folder: Path to the save folder.
        save_file_name: The filename to check (e.g. 'save_1.dat').
    
    Returns:
        Modification time as float (seconds since epoch), or None if file doesn't exist.
    """
    save_file = save_folder / save_file_name

    if save_file.exists():
        return os.path.getmtime(save_file)

    return None


def get_state_file_path() -> Path:
    """Return path to the JSON file storing last mtimes."""
    script_dir = Path(__file__).parent.resolve()
    return script_dir / ".last_mtimes.json"


def load_last_mtimes(state_file: Path) -> dict:
    """Load persisted last modification times for each save file."""
    if not state_file.exists():
        return {}

    try:
        with open(state_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Ensure keys are strings and values are floats (or None)
            return {str(k): (float(v) if v is not None else None) for k, v in data.items()}
    except Exception:
        return {}


def save_last_mtimes(state_file: Path, mtimes: dict) -> None:
    """Persist last modification times to disk."""
    try:
        with open(state_file, "w", encoding="utf-8") as f:
            json.dump(mtimes, f)
    except Exception as e:
        print(f"✗ Failed to save state file: {e}")


def create_backup(save_folder: Path, backup_folder: Path) -> Optional[Path]:
    """
    Create a timestamped backup of the save folder.
    
    Args:
        save_folder: Path to the save folder to backup.
        backup_folder: Path to the backups directory.
    
    Returns:
        Path to the created backup folder, or None if backup failed.
    """
    # Create timestamped backup folder name
    timestamp = int(time.time())
    backup_name = f"backup_{timestamp}"
    backup_path = backup_folder / backup_name
    
    try:
        print(f"Creating backup: {backup_path}")
        shutil.copytree(save_folder, backup_path, dirs_exist_ok=True)
        print(f"✓ Backup created successfully: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"✗ Failed to create backup: {e}")
        return None


def ensure_backup_folder() -> Path:
    """
    Ensure the backups folder exists next to the script.
    
    Returns:
        Path to the backups folder.
    """
    script_dir = Path(__file__).parent.resolve()
    backup_folder = script_dir / "backups"
    
    backup_folder.mkdir(exist_ok=True, parents=True)
    print(f"✓ Backups folder ready: {backup_folder}")
    
    return backup_folder


def format_time(timestamp: float) -> str:
    """
    Format a Unix timestamp to a readable datetime string.
    
    Args:
        timestamp: Seconds since epoch.
    
    Returns:
        Formatted datetime string.
    """
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")


# ============================================================================
# MAIN LOOP
# ============================================================================

def main():
    """Main backup loop."""
    print("=" * 70)
    print("Citizen Sleeper Auto-Save Backup Script")
    print("=" * 70)
    print(f"Operating System: {sys.platform}")
    print(f"Backup frequency: {BACKUP_FREQUENCY_SECONDS} seconds ({BACKUP_FREQUENCY_SECONDS // 60} minutes)")
    print()
    
    # Set up backups folder
    backup_folder = ensure_backup_folder()
    print()
    
    # Wait for save folder to appear
    save_folder = wait_for_save_folder()
    print()
    
    # Load persisted mtimes for each monitored save file
    state_file = get_state_file_path()
    last_mtimes = load_last_mtimes(state_file)

    # If we don't have a saved state, create an initial backup and record current mtimes
    if not state_file.exists():
        print("No previous state detected — creating initial backup if any save files exist...")
        any_exists = False
        current_snapshot = {}
        for fname in SAVE_FILE_NAMES:
            m = get_save_file_mtime(save_folder, fname)
            if m is not None:
                any_exists = True
            current_snapshot[fname] = m

        if any_exists:
            create_backup(save_folder, backup_folder)
        # Persist whatever we found (including None for missing files)
        save_last_mtimes(state_file, current_snapshot)
        last_mtimes = current_snapshot

    print("Starting backup monitoring loop...")
    print("-" * 70)
    print()

    # Main backup loop
    iteration = 0
    try:
        while True:
            iteration += 1
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{current_time}] Check #{iteration}")

            changed = False
            current_snapshot = {}

            # Check each monitored save file
            for fname in SAVE_FILE_NAMES:
                current_mtime = get_save_file_mtime(save_folder, fname)
                current_snapshot[fname] = current_mtime
                stored = last_mtimes.get(fname)

                if current_mtime is None and stored is None:
                    print(f"  {fname}: not present (no previous record)")
                    continue
                if current_mtime is None and stored is not None:
                    print(f"  {fname}: was present before, now missing (treating as change)")
                    changed = True
                    continue
                if stored is None and current_mtime is not None:
                    print(f"  {fname}: detected at {format_time(current_mtime)} (no previous record)")
                    changed = True
                    continue
                # Both exist
                if current_mtime is not None and current_mtime > stored:
                    print(f"  {fname}: modified! Previous: {format_time(stored)}, Current: {format_time(current_mtime)}")
                    changed = True
                else:
                    print(f"  {fname}: no change (last known {format_time(stored)})")

            if changed:
                print("  ⚡ Change detected in one or more save files — creating backup...")
                create_backup(save_folder, backup_folder)
                # update persisted mtimes
                last_mtimes = current_snapshot
                save_last_mtimes(state_file, last_mtimes)
            else:
                # No changes
                # Pick the most recent stored time for a user-friendly message, if any
                known_times = [t for t in last_mtimes.values() if t is not None]
                if known_times:
                    latest = max(known_times)
                    print(f"  ✓ No changes since {format_time(latest)}")
                else:
                    print("  ✓ No monitored save files present yet")

            # Wait before next check
            print(f"  Waiting {BACKUP_FREQUENCY_SECONDS} seconds until next check...")
            print()
            time.sleep(BACKUP_FREQUENCY_SECONDS)
    
    except KeyboardInterrupt:
        print()
        print("-" * 70)
        print("Backup script stopped by user.")
        sys.exit(0)
    except Exception as e:
        print()
        print("-" * 70)
        print(f"✗ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
