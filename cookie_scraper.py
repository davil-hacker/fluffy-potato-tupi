import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright
from config import *

# লগিং সেটআপ
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

async def scrape_toffee_cookies():
    """
    Toffee TV থেকে Cookie সংগ্রহ করে JSON ফাইলে সেভ করে
    """
    logger.info("🚀 Starting Toffee TV Cookie Scraper...")
    logger.info(f"🐍 Python version: {sys.version}")
    
    async with async_playwright() as p:
        # ব্রাউজার লঞ্চ - GitHub-এর জন্য অপটিমাইজড
        browser = await p.chromium.launch(
            headless=HEADLESS,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--disable-gpu',
                '--window-size=1920,1080'
            ]
        )
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        try:
            # স্টেপ ১: হোমপেজ ভিজিট
            logger.info(f"🌐 Navigating to: {BASE_URL}")
            await page.goto(BASE_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(PAGE_LOAD_WAIT * 1000)

            # স্টেপ ২: কুকি কনসেন্ট
            try:
                accept_buttons = await page.query_selector_all('button:has-text("Accept"), button:has-text("Accept All"), button:has-text("OK")')
                if accept_buttons:
                    await accept_buttons[0].click()
                    logger.info("✅ Accepted cookies")
                    await page.wait_for_timeout(2000)
                else:
                    logger.info("ℹ️ No cookie consent button found")
            except Exception as e:
                logger.info(f"ℹ️ Cookie consent handling skipped: {str(e)}")

            # স্টেপ ৩: ভিডিও পেজে যান
            logger.info(f"📺 Loading video page: {VIDEO_URL}")
            await page.goto(VIDEO_URL, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(VIDEO_LOAD_WAIT * 1000)

            # স্টেপ ৪: পেজের স্ক্রিনশট নিন (ডিবাগের জন্য)
            screenshot_path = "page_screenshot.png"
            await page.screenshot(path=screenshot_path)
            logger.info(f"📸 Screenshot saved: {screenshot_path}")

            # স্টেপ ৫: সব Cookie সংগ্রহ
            all_cookies = await context.cookies()
            logger.info(f"🍪 Total cookies collected: {len(all_cookies)}")

            # কুকির বিস্তারিত তথ্য
            cookie_details = []
            for cookie in all_cookies:
                cookie_info = {
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', ''),
                    'path': cookie.get('path', '/'),
                    'expires': cookie.get('expires', 'Session'),
                    'secure': cookie.get('secure', False),
                    'httpOnly': cookie.get('httpOnly', False),
                    'sameSite': cookie.get('sameSite', 'None')
                }
                cookie_details.append(cookie_info)

            # গুরুত্বপূর্ণ Cookie ফিল্টার
            important_cookies = []
            for cookie in all_cookies:
                if any(keyword in cookie['name'] for keyword in IMPORTANT_KEYWORDS):
                    important_cookies.append(cookie)

            logger.info(f"⭐ Important cookies found: {len(important_cookies)}")

            # JSON ফরম্যাটে সেভ
            cookie_data = {
                "scraped_at": datetime.now().isoformat(),
                "url": VIDEO_URL,
                "total_cookies": len(all_cookies),
                "important_count": len(important_cookies),
                "important_cookies": important_cookies,
                "all_cookies": cookie_details,
                "summary": {
                    "edge_cache_cookie": next((c for c in all_cookies if "Edge-Cache" in c['name']), None),
                    "session_cookie": next((c for c in all_cookies if "session" in c['name'].lower()), None),
                    "auth_cookie": next((c for c in all_cookies if "auth" in c['name'].lower()), None)
                }
            }

            with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
                json.dump(cookie_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Cookies saved to {OUTPUT_FILE}")

            # সারাংশ প্রিন্ট
            print("\n" + "="*60)
            print("📋 COOKIE SUMMARY")
            print("="*60)
            
            edge_cookie = cookie_data['summary']['edge_cache_cookie']
            if edge_cookie:
                print(f"🔑 Edge-Cache Cookie Found!")
                print(f"   Name: {edge_cookie['name']}")
                print(f"   Value: {edge_cookie['value'][:80]}...")
                print(f"   Expires: {edge_cookie.get('expires', 'Session')}")
            
            print(f"\n📊 Statistics:")
            print(f"   Total Cookies: {len(all_cookies)}")
            print(f"   Important: {len(important_cookies)}")
            print("="*60)

            return cookie_data

        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()

if __name__ == "__main__":
    print("="*60)
    print("🍪 TOFFEE TV COOKIE SCRAPER (GitHub Edition)")
    print("="*60)
    result = asyncio.run(scrape_toffee_cookies())
    if result:
        print("\n✅ Scraping completed successfully!")
        print(f"📁 Check '{OUTPUT_FILE}' for details")
    else:
        print("\n❌ Scraping failed!")
        sys.exit(1)
