import logging

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

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='category_and_subcategory_wise_product_scrape.log', 
    filemode='a'
)

def scrape_category_wise_products(categories):
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
    options.add_argument('--headless=new')
    # options.add_argument('--window-size=1920,1080')
    options.accept_insecure_certs = True
    driver = Chrome(version_main=141, options=options, seleniumwire_options=seleniumwire_options)
    site_url = "https://shopee.sg"
    driver.get(site_url)
    driver.maximize_window()
    try:
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        # logging.info(f"Successfully loaded initial site: {site_url}")
    except Exception as e:
        logging.error(f"Failed to load initial site {site_url}: {str(e)}")
    
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
    
    all_products_data = []  # Collect all products across categories
    
    for cat in categories:
        parent_catid = cat["parent_catid"]
        catid = cat["catid"]
        # logging.info(f"Processing category: parent={parent_catid}, catid={catid}")
        for i in range(2):  # Adjust range for more pages if needed
            page_url = f'https://shopee.sg/abc-cat.{parent_catid}.{catid}?page={i}&sortBy=sales'
            try:
                driver.get(page_url)
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                logging.info(f"Successfully loaded page: {page_url}")
            except Exception as e:
                logging.error(f"Failed to load page {page_url}: {str(e)}")
                continue  # Skip to next page if load fails
            
            human_simulate_incat = random.uniform(1, 7)
            simulate_human_behavior(driver, int(human_simulate_incat))
            driver.scopes = [r'.*shopee\.sg/api.*']
            # Extract product data
            products_data = []
            found_products = False
            for req in driver.requests:
                if "search/search_items?by=" in req.url and req.response:
                    # logging.info(f"Found Product API: {req.url}")
                    # logging.info(f"Status: {req.response.status_code}")
                    decoded_body = decode(req.response.body, req.response.headers.get('Content-Encoding', 'identity'))
                    body_text = decoded_body.decode('utf-8', errors='ignore')
                    
                    try:
                        data = json.loads(body_text)
                        # Extract product items
                        if 'items' in data:
                            for item_wrapper in data['items']:
                                if 'item_basic' in item_wrapper:
                                    item = item_wrapper['item_basic']
                                    
                                    # Extract the data you need, adding category info
                                    product_info = {
                                        "parent_catid": parent_catid,
                                        "catid": catid,
                                        "price": item.get('price', 0) / 100000,  # Convert to actual price
                                        "price_before_discount": item.get('price_before_discount', 0) / 100000,
                                        "raw_discount": item.get('raw_discount', 0),
                                        "discount_percentage": item.get('discount', '0%'),
                                        "name": item.get('name', ''),
                                        "image": f"https://down-sg.img.susercontent.com/file/{item.get('image', '')}",
                                        "sold": item.get('sold', 0),
                                        "historical_sold": item.get('historical_sold', 0),
                                        "shop_name": item.get('shop_name', ''),
                                        "itemid": item.get('itemid', ''),
                                        "shopid": item.get('shopid', ''),
                                        "rating_star": item.get('item_rating', {}).get('rating_star', 0),
                                        "rating_count": sum(item.get('item_rating', {}).get('rating_count', [0])),
                                        "shop_location": item.get('shop_location', ''),
                                        "stock": item.get('stock', 0),
                                    }
                                    
                                    products_data.append(product_info)
                            
                            found_products = True
                            logging.info(f"Extracted {len(products_data)} products from {page_url}")
                    except json.JSONDecodeError as e:
                        logging.error(f"JSON decode error for {req.url}: {str(e)}")
                    except Exception as e:
                        logging.error(f"Error processing response for {req.url}: {str(e)}")
            if found_products and products_data:
                all_products_data.extend(products_data)
            else:
                logging.warning(f"No products found for page: {page_url}")
    
    driver.quit()
    return all_products_data