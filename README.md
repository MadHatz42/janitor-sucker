# JanitorAI to Sucker.dev Character Sync

Automates the process of extracting characters from [JanitorAI.com](https://janitorai.com/) sending them to [sucker](https://sucker.severian.dev/) and downloading both the characters.json + the image separately. Designed for use with local AI hosting clients like [SillyTavern](https://github.com/SillyTavern/SillyTavern).

## Installation

### pipx (Recommended)

```bash
pipx install git+https://github.com/MadHatz42/janitor-sucker.git
```

After installation, run `janitor-dl` to start the interactive menu.

### AUR (Arch Linux)

<!-- AUR package coming soon -->

## Requirements

- Python 3.7+
- Firefox browser
- Selenium and Pillow (installed automatically with pipx)

## Quick Start

1. **Run the tool:**
   ```bash
   janitor-dl
   ```

2. **Set up your Firefox profile:**
   - Select option `2` from the menu to set up your Firefox profile
   - Choose an existing profile or create a new one (option `3`)
   - If creating a new profile, Firefox will automatically open with JanitorAI
   - Sign in to JanitorAI, then close Firefox completely

3. **Start syncing characters:**
   - Select option `1` from the menu to start character sync
   - When the browser opens, manually navigate to the character chat page you want to export
   - Press ENTER in the terminal when ready
   - The script will automatically:
     - Detect the character name
     - Send it to the chatbox
     - Open sucker.dev and download the JSON
     - Navigate back and download the character image

## Features

- **Interactive TUI Menu**: Easy-to-use text interface for all operations
- **Automated Profile Creation**: Create Firefox profiles directly from the tool
- **Automatic Browser Launch**: New profiles automatically open Firefox with JanitorAI
- **Profile Management**: Switch between Firefox profiles easily
- **Error Recovery**: Script loops on errors, allowing you to fix issues without restarting
- **Batch Processing**: Process multiple characters without restarting the browser

## Menu Options

The `janitor-dl` command provides an interactive menu with the following options:

1. **Start character sync** - Begin downloading characters from JanitorAI
2. **Setup Firefox profile** - Select or manage Firefox profiles for automation
3. **Create new Firefox profile** - Automatically create a new Firefox profile
4. **Exit** - Quit the application

## Notes

- Make sure Firefox is completely closed before running character sync
- If you get 403/Access Restricted errors, the profile may be blocked - create a new Firefox profile using option `3`
- The script loops on errors, so you can fix issues and continue without restarting
- Type 'quit' in the sync interface to exit
- It's recommended to create a dedicated Firefox profile for automation to avoid blocking your main profile

## Disclaimer

Currently from my testing Janitor does NOT ban your account if it detects a script, rather it might block the profile, thus the note about making new firefox profiles just in case!
But thats not to say this might change in the future! so before warned that I am NOT responsable if your account gets blocked, restricted or banned, while making the script i've tested it over 50 times with only my firefox profile getting blocked, but this current version should be the most undetectable yet! and so far I've experienced no issues with it! but don't come crying saying I didn't warn ya!
