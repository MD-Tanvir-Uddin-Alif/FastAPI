from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.undetected_chromedriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from seleniumwire.utils import decode
from urllib.parse import urlparse
from dotenv import load_dotenv
import random
import json
import time
import os

from behavior_function import simulate_human_behavior

def get_shopee_categories():
    """
    This function runs the entire Shopee category scraping process:
    - Sets up undetected Chrome with SeleniumWire
    - Loads cookies, handles popups, simulates human behavior
    - Navigates to categories page
    - Captures and extracts the 'get_category_tree' API response
    - Extracts catid, category_name, parent_catid, parent_category_name
    - Returns a list of dicts with the extracted data
    - Cleans up the driver
    """
    load_dotenv()
    email = os.getenv('shoppy_mail')
    password = os.getenv('shoppy_password')

    seleniumwire_options = {
        'verify_ssl': False  # Disable SSL verification to avoid backend errors
    }

    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.accept_insecure_certs = True  # Key addition to accept insecure certs

    driver = Chrome(version_main=141, options=options, seleniumwire_options=seleniumwire_options)

    site_url = "https://shopee.sg"
    driver.get(site_url)
    driver.maximize_window()

    # wait for page to load
    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )

    with open("shopee_seller.json", "r", encoding="utf-8") as f:
        cookies = json.load(f)

    def get_expiry(cookie):
        for key in ("expiry", "expirationDate", "expires", "expire", "expiration"):
            if key in cookie and cookie[key]:
                try:
                    return int(float(cookie[key]))
                except Exception:
                    pass
        return None

    current_host = urlparse(driver.current_url).hostname  

    added = 0
    for cookie in cookies:
        cookie_payload = {
            "name": cookie.get("name"),
            "value": cookie.get("value", ""),
        }

        if cookie.get("path"):
            cookie_payload["path"] = cookie["path"]
        if "secure" in cookie:
            cookie_payload["secure"] = bool(cookie["secure"])
        if "httpOnly" in cookie:
            cookie_payload["httpOnly"] = bool(cookie["httpOnly"])

        expiry = get_expiry(cookie)
        if expiry:
            cookie_payload["expiry"] = expiry

        domain = cookie.get("domain")
        if domain:
            normalized_domain = domain.lstrip(".")
            if normalized_domain == current_host:
                cookie_payload["domain"] = normalized_domain  # Use without leading dot to avoid invalid domain error
            else:
                continue  # Skip if domain doesn't match

        try:
            driver.add_cookie(cookie_payload)
            added += 1
        except Exception as e:
            print(f"Failed to add cookie {cookie.get('name')!r}: {e}. Payload: {cookie_payload}")

    print(f"Attempted to add {len(cookies)} cookies, successfully added {added} (approx).")
    time.sleep(1)
    driver.refresh()
    time.sleep(5)

    try:
        close_popUP = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="HomePagePopupBannerSection"]/div[2]/div'))
        )
        delay = random.uniform(0.5,0.9)
        actions = ActionChains(driver)
        actions.move_to_element(close_popUP).pause(delay).click().perform()
    except:
        print("dint got the popup")

    human_simulate = random.uniform(1,5)
    simulate_human_behavior(driver, int(human_simulate)) 

    driver.get('https://shopee.sg/all_categories')

    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    human_simulate_incat = random.uniform(1,5)
    simulate_human_behavior(driver, int(human_simulate_incat)) 

    driver.scopes = [r'.*shopee\.sg/api.*']  # Use raw string to fix SyntaxWarning

    # Hunt for the specific API
    found = False
    all_extracted = []  # Default empty list if not found
    for req in driver.requests:
        if "get_category_tree" in req.url.lower() and req.response:  # Case-insensitive match
            print(f"Found API: {req.url}")
            print(f"Method: {req.method}")
            print(f"Status: {req.response.status_code}")

            # Decode the response body (handles compression like gzip)
            decoded_body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            body_text = decoded_body.decode('utf-8', errors='ignore')

            try:
                data = json.loads(body_text)

                # Function to extract catid, category_name, parent_catid, parent_category_name
                def extract_categories(categories, extracted=[], parent_catid=None, parent_name=None):
                    for cat in categories:
                        extracted.append({
                            "catid": cat['catid'],
                            "category_name": cat['name'],
                            "parent_catid": parent_catid if parent_catid is not None else cat['parent_catid'],
                            "parent_category_name": parent_name if parent_name is not None else None
                        })
                        
                        # If children, recurse
                        if 'children' in cat and cat['children']:
                            extract_categories(cat['children'], extracted, cat['catid'], cat['name'])
                    
                    return extracted

                # Extract
                if 'data' in data and 'category_list' in data['data']:
                    all_extracted = extract_categories(data['data']['category_list'])
                else:
                    print("No category_list found!")

            except json.JSONDecodeError:
                print("Response isn't JSON? Raw content:\n", body_text)

            found = True
            break

    if not found:
        print("No 'get_category_tree' API found. Try increasing sleep time or check dev tools.")

    driver.quit() 

    return all_extracted 