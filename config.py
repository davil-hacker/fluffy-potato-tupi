# Toffee TV Cookie Scraper Configuration

# Target URLs
BASE_URL = "https://toffeelive.com/"
VIDEO_URL = "https://toffeelive.com/en/watch/DNMXs5UBm1RY_In7IJ72"

# Browser Settings
HEADLESS = True  # GitHub Actions-এ True রাখুন
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Cookie Filtering Keywords
IMPORTANT_KEYWORDS = ['Edge-Cache', 'token', 'session', 'auth', 'cf_', '__cf']

# Wait Times (seconds)
PAGE_LOAD_WAIT = 5
VIDEO_LOAD_WAIT = 8

# Output File
OUTPUT_FILE = "toffee_cookies.json"