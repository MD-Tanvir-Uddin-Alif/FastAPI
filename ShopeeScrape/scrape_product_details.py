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

def scrape_shopee_product(shop_id, product_id):
    load_dotenv()
    email = os.getenv('shoppy_mail')
    password = os.getenv('shoppy_password')

    seleniumwire_options = {
        'verify_ssl': False
    }

    options = ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.accept_insecure_certs = True

    driver = Chrome(version_main=141, options=options, seleniumwire_options=seleniumwire_options)

    site_url = "https://shopee.sg"
    driver.get(site_url)
    driver.maximize_window()

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
                cookie_payload["domain"] = normalized_domain
            else:
                continue

        try:
            driver.add_cookie(cookie_payload)
            added += 1
        except Exception as e:
            print(f"Failed to add cookie {cookie.get('name')!r}: {e}")

    print(f"Successfully added {added} cookies.")
    time.sleep(1)
    driver.refresh()
    time.sleep(5)

    try:
        close_popUP = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="HomePagePopupBannerSection"]/div[2]/div'))
        )
        delay = random.uniform(0.5, 0.9)
        actions = ActionChains(driver)
        actions.move_to_element(close_popUP).pause(delay).click().perform()
    except:
        print("No popup found")

    human_simulate = random.uniform(1, 7)
    simulate_human_behavior(driver, int(human_simulate)) 

    product_url = f'https://shopee.sg/abc-i.{shop_id}.{product_id}'
    driver.get(product_url)

    WebDriverWait(driver, 15).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    human_simulate_incat = random.uniform(1, 7)
    simulate_human_behavior(driver, int(human_simulate_incat)) 

    driver.scopes = [r'.*shopee\.sg/api.*']

    # Extract product data
    product_info = {}
    found_product = False

    for req in driver.requests:
        if "/get_pc?item_id=" in req.url and req.response:
            print(f"Found Product API: {req.url}")
            print(f"Status: {req.response.status_code}")

            decoded_body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
            body_text = decoded_body.decode('utf-8', errors='ignore')
            
            try:
                data = json.loads(body_text)

                # Extract product items
                if 'data' in data and 'item' in data['data']:
                    item = data['data']['item']  # Direct access to the item dict
                    
                    # Extract the data you need
                    product_info = {
                        # Price comparison data
                        'price': item.get('price', 0) / 100000,  # Convert to actual price
                        'price_before_discount': item.get('price_before_discount', 0) / 100000,
                        'raw_discount': item.get('raw_discount', 0),
                        'discount_percentage': item.get('show_discount', 0),  # Adjusted key, as 'discount' might not be present
                        
                        # Product listing data
                        'name': item.get('title', ''),  # Use 'title' instead of 'name'
                        'image': f"https://down-sg.img.susercontent.com/file/{item.get('image', '')}",
                        'sold': data['data']['product_review'].get('sold_count_display', '0').replace('+', '').replace('k', '000') if 'product_review' in data['data'] else 0,  # Use from product_review, convert '10k+' to 10000
                        'historical_sold': data['data']['product_review'].get('historical_sold_display', '0').replace('+', '').replace('k', '000') if 'product_review' in data['data'] else 0,  # Similar
                        
                        # Shop info
                        'shop_name': data['data']['shop_detailed'].get('name', '') if 'shop_detailed' in data['data'] else '',
                        
                        # Additional useful data
                        'itemid': item.get('item_id', ''),
                        'shopid': item.get('shop_id', ''),
                        'rating_star': item['item_rating'].get('rating_star', 0) if 'item_rating' in item else 0,
                        'rating_count': sum(item['item_rating'].get('rating_count', [0])) if 'item_rating' in item else 0,
                        'shop_location': item.get('shop_location', ''),
                        'stock': item.get('stock', 0),
                    }
                    
                    found_product = True
                    break  # Since it's a single product, no need to check further requests

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"Error processing response: {e}")

    driver.quit()
    
    if found_product:
        return product_info
    else:
        print("No product found.")
        return {}