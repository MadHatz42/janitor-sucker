# JanitorAI to Sucker.dev Character Sync

Automates the process of extracting characters from JanitorAI.com and downloading them to sucker.dev.

## Requirements

- Python 3.7+
- Firefox browser
- Selenium (`pip install selenium`)
- Pillow (`pip install pillow`)

## Setup

1. Install dependencies:
   ```bash
   pip install selenium pillow
   ```

2. Set up your Firefox profile:
   ```bash
   python setup_profile.py
   ```
   This will:
   - Find all your Firefox profiles
   - Let you select which one to use
   - Automatically update `sync.py` with the selected profile
   - Provide instructions if you need to create a new profile

   **Note:** If you're getting 403/Access Restricted errors, create a new Firefox profile specifically for automation to avoid blocking your main profile.

## Usage

1. Run the script:
   ```bash
   python sync.py
   ```

2. When the browser opens, **manually navigate** to JanitorAI and log in (this avoids automated navigation detection)

3. Navigate to the character chat page you want to export

4. Press ENTER in the terminal when ready

5. The script will:
   - Detect the character name
   - Send it to the chatbox
   - Open sucker.dev and download the JSON
   - Navigate back and download the character image

## Notes

- Make sure Firefox is completely closed before running the script
- If you get 403/Access Restricted errors, the profile may be blocked - try a different Firefox profile
- The script loops, so you can process multiple characters without restarting
- Type 'quit' to exit

