import asyncio
import json
import logging
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
    async with async_playwright() as p:
        logger.info("🚀 Starting Toffee TV Cookie Scraper...")
        
        # ব্রাউজার লঞ্চ
        browser = await p.chromium.launch(headless=HEADLESS)
        context = await browser.new_context(
            user_agent=USER_AGENT,
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()

        # নেটওয়ার্ক রিকোয়েস্ট মনিটর করার জন্য
        network_requests = []
        
        async def handle_request(request):
            if '.m3u8' in request.url or 'manifest' in request.url:
                network_requests.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': request.headers,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info(f"📡 Captured request: {request.url[:100]}...")
        
        page.on('request', handle_request)

        try:
            # স্টেপ ১: হোমপেজ ভিজিট
            logger.info(f"🌐 Navigating to: {BASE_URL}")
            await page.goto(BASE_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(PAGE_LOAD_WAIT * 1000)

            # স্টেপ ২: কুকি কনসেন্ট (যদি থাকে)
            try:
                await page.click("button:has-text('Accept')", timeout=5000)
                logger.info("✅ Accepted cookies")
                await page.wait_for_timeout(2000)
            except:
                logger.info("ℹ️ No cookie consent button found")

            # স্টেপ ৩: লগইন (প্রয়োজন হলে)
            # await login_to_toffee(page)

            # স্টেপ ৪: ভিডিও পেজে যান
            logger.info(f"📺 Loading video page: {VIDEO_URL}")
            await page.goto(VIDEO_URL, wait_until="domcontentloaded")
            
            # প্লেয়ার লোড হওয়ার জন্য অপেক্ষা
            await page.wait_for_timeout(VIDEO_LOAD_WAIT * 1000)

            # স্টেপ ৫: ভিডিও প্লেয়ার এলিমেন্ট চেক
            try:
                player = await page.query_selector('video, .player, #player')
                if player:
                    logger.info("✅ Video player found")
                else:
                    logger.warning("⚠️ Video player not found")
            except:
                pass

            # স্টেপ ৬: সব Cookie সংগ্রহ
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

            # স্টেপ ৭: JSON ফরম্যাটে সেভ
            cookie_data = {
                "scraped_at": datetime.now().isoformat(),
                "url": VIDEO_URL,
                "total_cookies": len(all_cookies),
                "important_count": len(important_cookies),
                "important_cookies": important_cookies,
                "all_cookies": cookie_details,
                "network_requests": network_requests,
                "summary": {
                    "edge_cache_cookie": next((c for c in all_cookies if "Edge-Cache" in c['name']), None),
                    "session_cookie": next((c for c in all_cookies if "session" in c['name'].lower()), None),
                    "auth_cookie": next((c for c in all_cookies if "auth" in c['name'].lower()), None)
                }
            }

            with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
                json.dump(cookie_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Cookies saved to {OUTPUT_FILE}")

            # স্টেপ ৮: গুরুত্বপূর্ণ তথ্য প্রিন্ট
            print("\n" + "="*60)
            print("📋 COOKIE SUMMARY")
            print("="*60)
            
            # Edge-Cache Cookie
            edge_cookie = cookie_data['summary']['edge_cache_cookie']
            if edge_cookie:
                print(f"🔑 Edge-Cache Cookie:")
                print(f"   Name: {edge_cookie['name']}")
                print(f"   Value: {edge_cookie['value'][:80]}...")
                print(f"   Expires: {edge_cookie.get('expires', 'Session')}")
                print(f"   Domain: {edge_cookie.get('domain', 'N/A')}")
            
            # সেশন Cookie
            session_cookie = cookie_data['summary']['session_cookie']
            if session_cookie:
                print(f"\n🔐 Session Cookie:")
                print(f"   Name: {session_cookie['name']}")
                print(f"   Value: {session_cookie['value'][:40]}...")
            
            print(f"\n📊 Statistics:")
            print(f"   Total Cookies: {len(all_cookies)}")
            print(f"   Important: {len(important_cookies)}")
            print(f"   Network Requests Captured: {len(network_requests)}")
            
            # কুকির মেয়াদ চেক
            if edge_cookie and edge_cookie.get('expires') and edge_cookie['expires'] != -1:
                import time
                current_time = int(time.time())
                expiry_time = int(edge_cookie['expires'])
                days_left = (expiry_time - current_time) // 86400
                if days_left > 0:
                    print(f"\n⏰ Cookie expires in {days_left} days")
                else:
                    hours_left = (expiry_time - current_time) // 3600
                    print(f"\n⏰ Cookie expires in {hours_left} hours" if hours_left > 0 else "⚠️ Cookie expired!")
            
            print("="*60)

            return cookie_data

        except Exception as e:
            logger.error(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()
            return None
        finally:
            await browser.close()

async def login_to_toffee(page):
    """লগইন ফাংশন (প্রয়োজন হলে)"""
    try:
        logger.info("🔐 Attempting to login...")
        await page.click("text=Sign In")
        await page.wait_for_timeout(2000)
        
        # ইমেইল এবং পাসওয়ার্ড দিন
        await page.fill("input[type='email']", "your_email@example.com")
        await page.fill("input[type='password']", "your_password")
        
        # লগইন বাটনে ক্লিক
        await page.click("button:has-text('Sign In')")
        await page.wait_for_timeout(5000)
        
        # লগইন সফল হয়েছে কিনা চেক
        try:
            await page.wait_for_selector("text=Sign Out", timeout=5000)
            logger.info("✅ Logged in successfully")
        except:
            logger.warning("⚠️ Login might have failed")
    except Exception as e:
        logger.warning(f"⚠️ Login failed: {str(e)}")

if __name__ == "__main__":
    print("="*60)
    print("🍪 TOFFEE TV COOKIE SCRAPER")
    print("="*60)
    result = asyncio.run(scrape_toffee_cookies())
    if result:
        print("\n✅ Scraping completed successfully!")
        print(f"📁 Check '{OUTPUT_FILE}' for details")
    else:
        print("\n❌ Scraping failed!")
