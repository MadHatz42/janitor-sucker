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
    
    profiles = []
    for item in firefox_dir.iterdir():
        if item.is_dir():
            # Look for profile directories (contain .default, .release, .automation, etc.)
            if re.search(r'\.(default|release|automation)', item.name):
                profiles.append(item)
    
    return sorted(profiles)

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
    current_profile = get_current_profile()
    if current_profile == profile_path:
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
    print("\nFinding Firefox profiles...\n")
    
    profiles = find_firefox_profiles()
    
    if not profiles:
        print("[ERROR] No Firefox profiles found!")
        print("\nIf you're getting 403 errors, you may need to:")
        print("1. Create a new Firefox profile")
        print("2. Sign in to JanitorAI in that profile")
        print("3. Run this script again to select it")
        return 1
    
    print("Available Firefox profiles:\n")
    for i, profile in enumerate(profiles, 1):
        profile_name = profile.name
        profile_path = f"~/.mozilla/firefox/{profile_name}"
        print(f"  {i}. {profile_name}")
        print(f"     {profile_path}\n")
    
    print(f"  {len(profiles) + 1}. Create instructions for a new profile\n")
    
    while True:
        try:
            choice = input(f"Select a profile (1-{len(profiles) + 1}): ").strip()
            choice_num = int(choice)
            
            if 1 <= choice_num <= len(profiles):
                selected_profile = profiles[choice_num - 1]
                profile_name = selected_profile.name
                profile_path = f"~/.mozilla/firefox/{profile_name}"
                
                print(f"\n[INFO] Selected profile: {profile_name}")
                
                success, status = update_sync_py(profile_path)
                
                if status == "already_in_use":
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
                print("\n" + "="*60)
                print("How to create a new Firefox profile:")
                print("="*60)
                print("\n1. Open Firefox")
                print("2. Type 'about:profiles' in the address bar")
                print("3. Click 'Create a New Profile'")
                print("4. Follow the wizard to create a new profile")
                print("5. Start Firefox with the new profile")
                print("6. Sign in to JanitorAI in that profile")
                print("7. Close Firefox")
                print("8. Run this script again to select the new profile")
                print("\nNote: It's recommended to create a profile specifically")
                print("      for automation to avoid blocking your main profile.")
                print("="*60 + "\n")
                continue
            else:
                print(f"[ERROR] Please enter a number between 1 and {len(profiles) + 1}")
        
        except ValueError:
            print("[ERROR] Please enter a valid number")
        except KeyboardInterrupt:
            print("\n[INFO] Cancelled.")
            return 1

if __name__ == "__main__":
    sys.exit(main())

