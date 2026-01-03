# JanitorAI to Sucker.dev Character Sync

Automates the process of extracting characters from [JanitorAI.com](https://janitorai.com/) sending them to [sucker](https://sucker.severian.dev/) and downloading both the characters.json + the image separately
Designed for use with local AI hosting clients like [SillyTavern](https://github.com/SillyTavern/SillyTavern)

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

## Disclaimer

Currently from my testing Janitor does NOT ban your account if it detects a script, rather it might block the profile, thus the note about making new firefox profiles just in case!
But thats not to say this might change in the future! so before warned that I am NOT responsable if your account gets blocked, restricted or banned, while making the script i've tested it over 50 times with only my firefox profile getting blocked, but this current version should be the most undetectable yet! and so far I've experienced no issues with it! but don't come crying saying I didn't warn ya!
