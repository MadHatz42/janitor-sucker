#!/usr/bin/env python3
"""
Module for creating new Firefox profiles programmatically.
"""

import os
import re
import string
import random
import subprocess
import sys
from pathlib import Path
from configparser import ConfigParser


def generate_profile_name(base_name="automation"):
    """Generate a unique profile directory name."""
    firefox_dir = Path.home() / ".mozilla" / "firefox"
    
    # Generate random 8-character string
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    profile_dir_name = f"{random_part}.{base_name}"
    
    # Ensure it's unique
    max_attempts = 10
    attempt = 0
    while (firefox_dir / profile_dir_name).exists() and attempt < max_attempts:
        random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        profile_dir_name = f"{random_part}.{base_name}"
        attempt += 1
    
    return profile_dir_name


def create_firefox_profile(profile_name=None):
    """
    Create a new Firefox profile programmatically.
    
    Args:
        profile_name: Optional base name for the profile (default: "automation")
    
    Returns:
        Path object to the created profile directory, or None on failure
    """
    firefox_dir = Path.home() / ".mozilla" / "firefox"
    
    if not firefox_dir.exists():
        firefox_dir.mkdir(parents=True, exist_ok=True)
    
    # Use provided name or default
    base_name = profile_name if profile_name else "automation"
    # Clean the base name (only alphanumeric and dots)
    base_name = re.sub(r'[^a-zA-Z0-9.]', '', base_name)
    if not base_name:
        base_name = "automation"
    
    # Generate unique directory name
    profile_dir_name = generate_profile_name(base_name)
    profile_path = firefox_dir / profile_dir_name
    
    try:
        # Get list of existing profiles before creation
        existing_profiles = set(item.name for item in firefox_dir.iterdir() if item.is_dir())
        
        # Method 1: Try using Firefox's -CreateProfile command (most reliable)
        print(f"[INFO] Creating Firefox profile...")
        
        # Run firefox -CreateProfile (this doesn't open Firefox GUI)
        # Note: Firefox creates profiles with a random 8-char prefix
        result = subprocess.run(
            ["firefox", "-CreateProfile", f"{base_name}"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # Firefox creates profiles with a random prefix, so find the newly created one
        # Check for new directories that end with our base name
        new_profiles = []
        for item in firefox_dir.iterdir():
            if item.is_dir() and item.name not in existing_profiles:
                if item.name.endswith(f".{base_name}"):
                    new_profiles.append(item)
        
        if new_profiles:
            # Use the most recently created one (should only be one)
            new_profile = max(new_profiles, key=lambda p: p.stat().st_mtime)
            print(f"[SUCCESS] Created profile: {new_profile.name}")
            return new_profile
        
        # Fallback: Create directory manually and update profiles.ini
        print(f"[INFO] Using fallback method to create profile...")
        profile_path.mkdir(exist_ok=True)
        
        # Create minimal prefs.js (Firefox will initialize this on first run)
        prefs_js = profile_path / "prefs.js"
        if not prefs_js.exists():
            prefs_js.write_text('// Firefox preferences - will be initialized on first run\n')
        
        # Update profiles.ini
        profiles_ini = firefox_dir / "profiles.ini"
        config = ConfigParser()
        
        if profiles_ini.exists():
            config.read(profiles_ini)
        else:
            # Create new profiles.ini
            config.add_section('General')
            config.set('General', 'StartWithLastProfile', '1')
        
        # Find the next profile number
        profile_numbers = []
        for section in config.sections():
            if section.startswith('Profile'):
                try:
                    num = int(section.replace('Profile', ''))
                    profile_numbers.append(num)
                except ValueError:
                    pass
        
        next_num = max(profile_numbers) + 1 if profile_numbers else 0
        profile_section = f'Profile{next_num}'
        
        config.add_section(profile_section)
        config.set(profile_section, 'Name', base_name)
        config.set(profile_section, 'IsRelative', '1')
        config.set(profile_section, 'Path', profile_dir_name)
        
        # Write profiles.ini
        with open(profiles_ini, 'w') as f:
            config.write(f, space_around_delimiters=False)
        
        print(f"[SUCCESS] Created profile: {profile_dir_name}")
        return profile_path
        
    except subprocess.TimeoutExpired:
        print("[ERROR] Firefox command timed out")
        return None
    except FileNotFoundError:
        print("[ERROR] Firefox not found. Please install Firefox.")
        return None
    except Exception as e:
        print(f"[ERROR] Failed to create profile: {e}")
        import traceback
        traceback.print_exc()
        return None


def launch_firefox_with_profile(profile_path, url="https://janitorai.com"):
    """
    Launch Firefox with a specific profile and URL.
    Uses normal Firefox (not Selenium) to avoid detection.
    """
    try:
        # Use -profile flag with full path to specify the profile
        # -new-instance ensures it opens in a new window even if Firefox is running
        cmd = ["firefox", "-profile", str(profile_path), "-new-instance", url]
        
        # Launch in background (detached process)
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return True
    except FileNotFoundError:
        print("[ERROR] Firefox not found. Please install Firefox.")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to launch Firefox: {e}")
        return False


def main():
    """Interactive function to create a new profile."""
    print("="*60)
    print(" " * 15 + "Create Firefox Profile")
    print("="*60)
    print("\nThis will create a new Firefox profile for automation.")
    print("After creation, Firefox will automatically open with JanitorAI.")
    print("You'll need to:")
    print("1. Sign in to JanitorAI in the opened Firefox window")
    print("2. Close Firefox completely")
    print("3. Select this profile in the setup menu\n")
    
    profile_name = input("Enter a name for the profile (or press ENTER for 'automation'): ").strip()
    if not profile_name:
        profile_name = "automation"
    
    profile_path = create_firefox_profile(profile_name)
    
    if profile_path:
        print(f"\n[SUCCESS] Profile created successfully!")
        print(f"Profile path: {profile_path}")
        print(f"\n[INFO] Launching Firefox with the new profile...")
        
        # Launch Firefox with the profile and open JanitorAI
        if launch_firefox_with_profile(profile_path):
            print(f"[SUCCESS] Firefox launched!")
            print(f"\nNext steps:")
            print(f"1. Sign in to JanitorAI in the opened Firefox window")
            print(f"2. Close Firefox completely when done")
            print(f"3. Run the setup profile option to select this profile")
        else:
            print(f"\n[WARNING] Could not launch Firefox automatically.")
            print(f"Please manually start Firefox with this profile:")
            print(f"   firefox -profile {profile_path} https://janitorai.com")
        
        return 0
    else:
        print("\n[ERROR] Failed to create profile.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

