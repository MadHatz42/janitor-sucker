import time
import os
import sys
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from PIL import Image
from io import BytesIO

# --- CONFIGURATION ---
# Set your Firefox profile path (find it in ~/.mozilla/firefox/)
# Example: "~/.mozilla/firefox/yvntn2wj.automation"
PROFILE_PATH = os.path.expanduser("~/.mozilla/firefox/p6tus3mi.a2")
DOWNLOAD_PATH = os.path.expanduser("~/Downloads")

def get_firefox_driver():
    # Use existing profile - try to modify as little as possible to avoid detection
    if PROFILE_PATH and os.path.exists(PROFILE_PATH):
        profile = FirefoxProfile(PROFILE_PATH)
        print(f"[INFO] Using Firefox profile: {PROFILE_PATH}")
    else:
        profile = FirefoxProfile()
        print("[WARNING] Profile path not found, using default profile")
    
    # Only set essential download preferences (minimal changes to avoid detection)
    profile.set_preference("browser.download.folderList", 2)
    profile.set_preference("browser.download.manager.showWhenStarting", False)
    profile.set_preference("browser.download.dir", DOWNLOAD_PATH)
    profile.set_preference("browser.helperApps.neverAsk.saveToDisk", "application/json")
    
    # Update the profile (required after setting preferences)
    profile.update_preferences()
    
    # Assign profile to options (Selenium 4.x way)
    options = Options()
    options.profile = profile
    
    service = Service(log_output=os.devnull)
    driver = webdriver.Firefox(options=options, service=service)
    
    return driver

def detect_character_name(driver):
    """Try multiple methods to detect the character name."""
    wait = WebDriverWait(driver, 5)
    
    # Method 1: Parse from tab title (most reliable)
    try:
        title = driver.title.strip()
        if title:
            if '(' in title:
                name = title.split('(')[0].strip()
            elif '|' in title:
                name = title.split('|')[0].strip()
            else:
                name = title.strip()
            
            if name and len(name) < 100:
                return name
    except Exception as e:
        print(f"[DEBUG] Title parsing failed: {e}")
    
    # Method 2: Look for button in navigation bar
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
        for button in buttons:
            text = button.text.strip()
            if text and len(text) < 50 and text not in ["Back", "Menu", "Settings", "Login"]:
                if ' ' not in text or len(text.split()[0]) < 20:
                    return text.split()[0]
    except:
        pass
    
    # Method 3: Look for name in chat area
    selectors = [
        "span.font-bold",
        "span[class*='font-bold']",
        "div[class*='character-name']",
        "div[class*='char-name']",
        "h1", "h2", "h3",
        "[class*='name']"
    ]
    
    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                text = element.text.strip()
                if text and len(text) < 50 and text not in ["Back", "Login", "Settings", "Menu"]:
                    if element.is_displayed():
                        name = text.split()[0] if ' ' in text else text
                        if len(name) < 30:
                            return name
        except:
            continue
    
    # Method 4: Look in URL
    try:
        url = driver.current_url
        if '/character/' in url:
            parts = url.split('/character/')
            if len(parts) > 1:
                name = parts[1].split('/')[0].strip()
                if name:
                    return name
    except:
        pass
    
    raise Exception("Could not detect character name")

def find_chatbox(driver):
    """Find the chatbox element."""
    wait = WebDriverWait(driver, 5)
    
    selectors = [
        "textarea",
        "textarea[placeholder*='message']",
        "textarea[placeholder*='Message']",
        "textarea[class*='chat']",
        "textarea[class*='input']",
        "textarea[role='textbox']"
    ]
    
    for selector in selectors:
        try:
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            if element.is_displayed() and element.is_enabled():
                return element
        except:
            continue
    
    raise Exception("Could not find chatbox")

def find_character_in_sucker(driver, char_name):
    """Find and scroll to the character in sucker.dev, then click download JSON."""
    wait = WebDriverWait(driver, 10)
    
    time.sleep(2)
    
    # Scroll to bottom FIRST (newest characters are at the bottom)
    print("[SUCKER] Scrolling to bottom first...")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)
    
    xpaths = [
        f"//div[contains(text(), '{char_name}')]//button[contains(text(), 'Download JSON')]",
        f"//*[contains(text(), '{char_name}')]//following::button[contains(text(), 'Download JSON')]",
        f"//button[contains(text(), 'Download JSON')][ancestor::*[contains(text(), '{char_name}')]]"
    ]
    
    # Now search from the bottom
    print(f"[SUCKER] Searching for '{char_name}'...")
    for xpath in xpaths:
        try:
            button = driver.find_element(By.XPATH, xpath)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
            time.sleep(0.5)
            button.click()
            return True
        except:
            continue
    
    # If not found, scroll up and search
    print(f"[SUCKER] Not found at bottom, searching upward...")
    scroll_attempts = 0
    max_scrolls = 30
    
    while scroll_attempts < max_scrolls:
        for xpath in xpaths:
            try:
                button = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(0.5)
                button.click()
                return True
            except:
                continue
        
        driver.execute_script("window.scrollBy(0, -300);")
        time.sleep(0.3)
        scroll_attempts += 1
    
    raise Exception(f"Could not find character '{char_name}' in sucker.dev")

def find_back_button(driver):
    """Find and click the back button."""
    wait = WebDriverWait(driver, 5)
    
    selectors = [
        "button[aria-label*='Back' i]",
        "a[aria-label*='Back' i]",
        "[class*='back'] button",
        "[class*='back'] a"
    ]
    
    for selector in selectors:
        try:
            element = driver.find_element(By.CSS_SELECTOR, selector)
            if element.is_displayed() and element.is_enabled():
                element.click()
                return True
        except:
            continue
    
    # Fallback to browser back
    driver.back()
    return True

def find_character_image_url(driver):
    """Find the character image URL using Selenium element detection."""
    print("[IMAGE] Searching for character image using element detection...")
    wait = WebDriverWait(driver, 10)
    
    # Get page dimensions
    page_width = driver.execute_script("return document.body.scrollWidth")
    page_height = driver.execute_script("return document.body.scrollHeight")
    
    # Find all images using Selenium
    all_images = driver.find_elements(By.TAG_NAME, "img")
    candidates = []
    
    for img in all_images:
        try:
            if not img.is_displayed():
                continue
            
            size = img.size
            location = img.location
            width = size['width']
            height = size['height']
            
            # Character images are large (at least 200x200)
            if width >= 200 and height >= 200:
                x_ratio = location['x'] / page_width if page_width > 0 else 0.5
                y_ratio = location['y'] / page_height if page_height > 0 else 0
                
                # Prefer images on left side and not in header
                if x_ratio < 0.6 and y_ratio > 0.1:
                    area = width * height
                    candidates.append({
                        'element': img,
                        'src': img.get_attribute('src'),
                        'area': area,
                        'x': location['x']
                    })
        except:
            continue
    
    if candidates:
        # Sort by area (largest first), then by x position
        candidates.sort(key=lambda x: (-x['area'], x['x']))
        img_url = candidates[0]['src']
        print(f"[IMAGE] Found character image URL: {img_url[:80]}...")
        return img_url
    
    # Fallback: try any large image
    print("[IMAGE] Fallback: Looking for any large image...")
    for img in all_images:
        try:
            if img.is_displayed():
                size = img.size
                if size['width'] >= 200 and size['height'] >= 200:
                    img_url = img.get_attribute('src')
                    if img_url:
                        print(f"[IMAGE] Found large image (fallback): {img_url[:80]}...")
                        return img_url
        except:
            continue
    
    raise Exception("Could not find character image URL")

def download_and_convert_image(driver, char_name):
    """Download image: Open in new tab, find img element, screenshot just that element."""
    img_url = find_character_image_url(driver)
    
    if not img_url:
        raise Exception("Could not find image URL")
    
    print("[IMAGE] Opening image in new tab...")
    
    original_window = driver.current_window_handle
    
    driver.execute_script(f"window.open('{img_url}', '_blank');")
    time.sleep(1)
    
    windows = driver.window_handles
    image_window = [w for w in windows if w != original_window][0]
    driver.switch_to.window(image_window)
    time.sleep(2)
    
    print("[IMAGE] Finding image element on page...")
    wait = WebDriverWait(driver, 10)
    try:
        img_element = wait.until(EC.presence_of_element_located((By.TAG_NAME, "img")))
        print("[IMAGE] Found img element, taking screenshot of just the image...")
    except:
        driver.close()
        driver.switch_to.window(original_window)
        raise Exception("Could not find img element on image page")
    
    save_path = os.path.join(DOWNLOAD_PATH, f"{char_name}.png")
    print(f"[IMAGE] Saving image to {save_path}...")
    
    try:
        img_element.screenshot(save_path)
        print(f"[SUCCESS] Image saved as PNG: {save_path}")
    except Exception as e:
        driver.close()
        driver.switch_to.window(original_window)
        print(f"[ERROR] Element screenshot failed: {e}")
        raise
    
    driver.close()
    driver.switch_to.window(original_window)
    time.sleep(0.5)
    
    return save_path

def main():
    print("[INIT] Launching Firefox via Selenium...")
    driver = get_firefox_driver()
    
    try:
        print("[INFO] Browser opened. Please navigate to JanitorAI manually.")
        print("[INFO] This avoids automated navigation detection.")
        print("[INFO] Once you're on the JanitorAI page, press ENTER to continue.")
        
        # Main loop - restart on errors
        while True:
            try:
                print("\n" + "="*60)
                print(" " * 15 + "WAITING FOR USER")
                print("="*60)
                print("  Instructions:")
                print("  1. Navigate to the character chat page in the browser")
                print("  2. Wait for the page to fully load")
                print("  3. Press ENTER when ready")
                print("\n  (Type 'quit' to exit)")
                print("="*60 + "\n")
                user_input = sys.stdin.readline().strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("[INFO] Exiting...")
                    break
                
                print("[INFO] Waiting for page to stabilize...")
                time.sleep(2)
                
                # Step 1: Detect character name
                print("\n[STEP 1] Detecting character name...")
                char_name = detect_character_name(driver)
                print(f"[SUCCESS] Character name detected: {char_name}")
                
                # Step 2: Paste name into chatbox and send
                print("\n[STEP 2] Pasting character name into chatbox...")
                chatbox = find_chatbox(driver)
                chatbox.click()
                time.sleep(0.8)
                chatbox.clear()
                chatbox.send_keys(char_name)
                time.sleep(0.5)
                chatbox.send_keys(Keys.ENTER)
                print("[SUCCESS] Name sent to chatbox")
                time.sleep(2)
                
                # Step 3: Open sucker.dev in new tab
                print("\n[STEP 3] Opening sucker.dev in new tab...")
                janitor_window = driver.current_window_handle
                driver.execute_script("window.open('https://sucker.severian.dev/', '_blank');")
                time.sleep(1)
                
                windows = driver.window_handles
                sucker_window = [w for w in windows if w != janitor_window][0]
                driver.switch_to.window(sucker_window)
                time.sleep(3)
                
                # Step 4: Find character and download JSON
                print(f"\n[STEP 4] Searching for '{char_name}' in sucker.dev...")
                find_character_in_sucker(driver, char_name)
                print(f"[SUCCESS] JSON download initiated")
                time.sleep(2)
                
                # Close sucker tab and return to JanitorAI
                driver.close()
                driver.switch_to.window(janitor_window)
                time.sleep(1)
                
                # Step 5: Click back button
                print("\n[STEP 5] Navigating back...")
                try:
                    find_back_button(driver)
                    print("[SUCCESS] Navigated back")
                    time.sleep(2)
                except Exception as e:
                    print(f"[WARNING] Back button issue (using browser back): {e}")
                    driver.back()
                    time.sleep(2)
                
                # Step 6: Download and convert image
                print("\n[STEP 6] Downloading character image...")
                download_and_convert_image(driver, char_name)
                
                print("\n" + "="*60)
                print(" " * 18 + "SUCCESS!")
                print("="*60)
                print(f"  JSON downloaded to: {DOWNLOAD_PATH}")
                print(f"  Image saved as: {char_name}.png")
                print("\n  Ready for next character. Press ENTER to continue.")
                print("  (Type 'quit' to exit)")
                print("="*60 + "\n")
                
            except KeyboardInterrupt:
                print("\n[INFO] Interrupted by user. Exiting...")
                break
            except Exception as e:
                print(f"\n[ERROR] An error occurred: {e}")
                import traceback
                traceback.print_exc()
                print("\n  Returning to start. Fix the issue and press ENTER to try again.")
                print("  (Type 'quit' to exit)\n")
                # Close any extra tabs
                try:
                    windows = driver.window_handles
                    if len(windows) > 1:
                        current = driver.current_window_handle
                        for window in windows:
                            if window != current:
                                driver.switch_to.window(window)
                                driver.close()
                        driver.switch_to.window(windows[0])
                except:
                    pass
                continue
        
    except Exception as e:
        print(f"\n[CRASH] Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n[DONE] Script finished. Browser window remains open.")
        # Uncomment to auto-close: driver.quit()

if __name__ == "__main__":
    main()
