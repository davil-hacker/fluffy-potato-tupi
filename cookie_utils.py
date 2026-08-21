import json
import time
from datetime import datetime
from typing import List, Dict, Optional

def load_cookies_from_file(filename: str = "toffee_cookies.json") -> List[Dict]:
    """JSON ফাইল থেকে Cookie লোড করে"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('all_cookies', [])
    except FileNotFoundError:
        print(f"❌ File '{filename}' not found")
        return []

def get_cookie_value(cookies: List[Dict], cookie_name: str) -> Optional[str]:
    """নির্দিষ্ট নামের Cookie-র মান বের করে"""
    for cookie in cookies:
        if cookie.get('name') == cookie_name:
            return cookie.get('value')
    return None

def format_cookies_for_curl(cookies: List[Dict]) -> str:
    """cURL কমান্ডের জন্য Cookie ফরম্যাট করে"""
    cookie_strings = []
    for cookie in cookies:
        cookie_strings.append(f"{cookie['name']}={cookie['value']}")
    return "; ".join(cookie_strings)