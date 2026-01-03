#!/usr/bin/env python3
"""
Helper script to find Firefox profiles and update sync.py with the selected profile.
"""

import os
import re
import sys
from pathlib import Path

def find_firefox_profiles():
    """Find all Firefox profiles in the default location."""
    firefox_dir = Path.home() / ".mozilla" / "firefox"
    
    if not firefox_dir.exists():
        print("[ERROR] Firefox profiles directory not found!")
        return []
    
    # Exclude system directories
    excluded = {"Crash Reports", "Pending Pings", "Profile Groups"}
    
    profiles = []
    for item in firefox_dir.iterdir():
        if not item.is_dir():
            continue
        
        # Skip excluded directories
        if item.name in excluded:
            continue
        
        # Firefox profiles typically have a pattern like:
        # - name.default
        # - name.default-release
        # - name.default-default
        # - name.automation
        # - Or just any directory that contains a prefs.js file (indicates it's a profile)
        profile_prefs = item / "prefs.js"
        if profile_prefs.exists():
            # This is a valid Firefox profile
            profiles.append(item)
        elif re.search(r'\.(default|release|automation)', item.name):
            # Also include directories matching common profile patterns
            # even if prefs.js doesn't exist yet (newly created)
            profiles.append(item)
    
    return sorted(profiles, key=lambda x: x.stat().st_mtime, reverse=True)  # Sort by modification time, newest first

def get_current_profile():
    """Get the current PROFILE_PATH from sync.py."""
    sync_py_path = Path(__file__).parent / "sync.py"
    
    if not sync_py_path.exists():
        return None
    
    # Read the file
    with open(sync_py_path, 'r') as f:
        content = f.read()
    
    # Extract current PROFILE_PATH
    match = re.search(r'PROFILE_PATH = os\.path\.expanduser\("([^"]+)"\)', content)
    if match:
        return match.group(1)
    
    return None

def update_sync_py(profile_path):
    """Update the PROFILE_PATH in sync.py."""
    sync_py_path = Path(__file__).parent / "sync.py"
    
    if not sync_py_path.exists():
        print(f"[ERROR] sync.py not found at {sync_py_path}")
        return False, "not_found"
    
    # Check if this profile is already in use
    # Normalize paths by expanding tildes for comparison
    current_profile = get_current_profile()
    if current_profile:
        current_expanded = os.path.expanduser(current_profile)
        new_expanded = os.path.expanduser(profile_path)
        # Compare both raw and expanded paths
        # Use Path.resolve() to handle any symlinks or relative path issues
        try:
            current_resolved = Path(current_expanded).resolve()
            new_resolved = Path(new_expanded).resolve()
            if current_profile == profile_path or current_resolved == new_resolved:
                return False, "already_in_use"
        except Exception:
            # If path resolution fails, fall back to string comparison
            if current_profile == profile_path or current_expanded == new_expanded:
                return False, "already_in_use"
    
    # Read the file
    with open(sync_py_path, 'r') as f:
        content = f.read()
    
    # Replace the PROFILE_PATH line
    # Match: PROFILE_PATH = os.path.expanduser("...")
    pattern = r'PROFILE_PATH = os\.path\.expanduser\(".*"\)'
    replacement = f'PROFILE_PATH = os.path.expanduser("{profile_path}")'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content == content:
        return False, "not_found_in_file"
    
    # Write back
    with open(sync_py_path, 'w') as f:
        f.write(new_content)
    
    return True, "success"

def main():
    print("="*60)
    print(" " * 10 + "Firefox Profile Setup")
    print("="*60)
    print("\n[INFO] If you've used this script before and are getting 403 errors,")
    print("       create a new Firefox profile and select it here.")
    print("="*60)
    
    # Scan for profiles (can rescan if needed)
    while True:
        print("\nScanning for Firefox profiles...\n")
        profiles = find_firefox_profiles()
        
        if not profiles:
            print("[ERROR] No Firefox profiles found!")
            print("\nIf you're getting 403 errors, you may need to:")
            print("1. Create a new Firefox profile")
            print("2. Sign in to JanitorAI in that profile")
            print("3. Close Firefox and run this script again")
            return 1
        
        print("Available Firefox profiles:\n")
        for i, profile in enumerate(profiles, 1):
            profile_name = profile.name
            profile_path = f"~/.mozilla/firefox/{profile_name}"
            # Check if it's a fully initialized profile
            has_prefs = (profile / "prefs.js").exists()
            status = "✓" if has_prefs else "⚠ (new/incomplete)"
            print(f"  {i}. {profile_name} {status}")
            print(f"     {profile_path}\n")
        
        print(f"  {len(profiles) + 1}. Rescan for profiles")
        print(f"  {len(profiles) + 2}. Create instructions for a new profile")
        print(f"  0. Go back to main menu\n")
        
        while True:
            try:
                choice = input(f"Select an option (0-{len(profiles) + 2}): ").strip()
                choice_num = int(choice)
                
                if choice_num == 0:
                    # Go back to main menu
                    print("\n[INFO] Returning to main menu...\n")
                    return 0
                
                if 1 <= choice_num <= len(profiles):
                    selected_profile = profiles[choice_num - 1]
                    profile_name = selected_profile.name
                    profile_path = f"~/.mozilla/firefox/{profile_name}"
                    
                    print(f"\n[INFO] Selected profile: {profile_name}")
                    
                    # Check what's currently in sync.py for debugging
                    current_profile = get_current_profile()
                    if current_profile:
                        print(f"[DEBUG] Current profile in sync.py: {current_profile}")
                        print(f"[DEBUG] Selected profile path: {profile_path}")
                    
                    success, status = update_sync_py(profile_path)
                    
                    if status == "already_in_use":
                        # Verify the paths actually match by expanding them
                        if current_profile:
                            current_expanded = os.path.expanduser(current_profile)
                            new_expanded = os.path.expanduser(profile_path)
                            if current_expanded == new_expanded:
                                print(f"[INFO] This profile is already in use in sync.py")
                                print(f"       No changes needed. You can run sync.py with this profile.")
                            else:
                                # Paths don't actually match, force update
                                print(f"[WARNING] Profile path mismatch detected. Updating sync.py...")
                                # Force update by bypassing the check
                                sync_py_path = Path(__file__).parent / "sync.py"
                                with open(sync_py_path, 'r') as f:
                                    content = f.read()
                                pattern = r'PROFILE_PATH = os\.path\.expanduser\(".*"\)'
                                replacement = f'PROFILE_PATH = os.path.expanduser("{profile_path}")'
                                new_content = re.sub(pattern, replacement, content)
                                with open(sync_py_path, 'w') as f:
                                    f.write(new_content)
                                print(f"[SUCCESS] Updated sync.py with profile: {profile_path}")
                        else:
                            print(f"[INFO] This profile is already in use in sync.py")
                            print(f"       No changes needed. You can run sync.py with this profile.")
                        return 0
                    elif success:
                        print(f"[SUCCESS] Updated sync.py with profile: {profile_path}")
                        print("\nYou can now run sync.py with this profile.")
                        return 0
                    elif status == "not_found_in_file":
                        print("[ERROR] Could not find PROFILE_PATH line in sync.py")
                        return 1
                    else:
                        print("[ERROR] Failed to update sync.py")
                        return 1
                
                elif choice_num == len(profiles) + 1:
                    # Rescan for profiles
                    print("\nRescanning for profiles...\n")
                    break  # Break inner loop to rescan
                
                elif choice_num == len(profiles) + 2:
                    print("\n" + "="*60)
                    print("How to create a new Firefox profile:")
                    print("="*60)
                    print("\n1. Open Firefox")
                    print("2. Type 'about:profiles' in the address bar")
                    print("3. Click 'Create a New Profile'")
                    print("4. Follow the wizard to create a new profile")
                    print("5. Start Firefox with the new profile")
                    print("6. Sign in to JanitorAI in that profile")
                    print("7. Close Firefox completely")
                    print("8. Select option to rescan profiles in this script")
                    print("\nNote: It's recommended to create a profile specifically")
                    print("      for automation to avoid blocking your main profile.")
                    print("="*60 + "\n")
                    continue
                else:
                    print(f"[ERROR] Please enter a number between 0 and {len(profiles) + 2}")
            
            except ValueError:
                print("[ERROR] Please enter a valid number")
            except KeyboardInterrupt:
                print("\n[INFO] Cancelled.")
                return 1

if __name__ == "__main__":
    sys.exit(main())