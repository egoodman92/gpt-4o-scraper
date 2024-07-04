import sys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import os

# Check if URL is provided
if len(sys.argv) < 3:
    print("Usage: python3 1_gpt-web-scraper.py <NYT_URL> <ARTICLE_DIR>")
    sys.exit(1)

NYT_URL = sys.argv[1]
ARTICLE_DIR = sys.argv[2]

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Use your existing Chrome profile
chrome_profile_path = "/Users/emmettgoodman/Library/Application Support/Google/Chrome/Default"
chrome_options.add_argument(f"user-data-dir={chrome_profile_path}")

# Ensure images are enabled
prefs = {
    "profile.managed_default_content_settings.images": 1
}
chrome_options.add_experimental_option("prefs", prefs)

# Path to your ChromeDriver
chrome_driver_path = '/Users/emmettgoodman/Documents/projects/nyt-bot/political-chat/chromedriver/chromedriver-mac-arm64/chromedriver'

# Initialize WebDriver
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Navigate to the specific article
driver.get(NYT_URL)

# Wait for the page to load
time.sleep(5)

# Create directory for images if it doesn't exist
images_dir = os.path.join(ARTICLE_DIR, 'images')
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Get the viewport height
viewport_height = driver.execute_script("return window.innerHeight")

# Define the overlap amount
overlap = 100

# Scroll incrementally and take screenshots
scroll_pause_time = 0.5  # Adjust the pause time as needed
screenshot_count = 0  # Counter for screenshots

# Get the current scroll height
current_scroll_position = 0
new_height = driver.execute_script("return document.body.scrollHeight")

while current_scroll_position <= new_height:
    # Take a screenshot
    screenshot_path = os.path.join(images_dir, f'screenshot_{screenshot_count}.png')
    driver.save_screenshot(screenshot_path)
    screenshot_count += 1
    
    # Scroll down by viewport_height - overlap pixels
    driver.execute_script(f"window.scrollBy(0, {viewport_height - overlap});")
    
    # Wait to load page
    time.sleep(scroll_pause_time)
    
    # Update the current scroll position
    current_scroll_position += (viewport_height - overlap)
    
    # Update new scroll height after scrolling
    new_height = driver.execute_script("return document.body.scrollHeight")

# Close the browser
driver.quit()
