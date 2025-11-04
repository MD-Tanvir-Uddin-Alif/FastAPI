from playwright.sync_api import sync_playwright  # Notice: sync_playwright, not async
import asyncio
import time


# ---------- SYNCHRONOUS SCRAPER (no async/await here) ----------
def Scrape_product(name, results):
    """Simple synchronous function - no async needed"""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        for page_num in range(1, 11):
            print(f"\n  Scraping {name} | Page {page_num}")
            page.goto(
                f"https://www.flipkart.com/search?q={name}&otracker=search&page={page_num}",
                wait_until="domcontentloaded"
            )

            last_height = page.evaluate("document.body.scrollHeight")
            while True:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(1)  # Regular sleep, not asyncio.sleep
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            PageProducts = page.locator("div._75nlfW")
            count = PageProducts.count()

            for i in range(count):
                product = PageProducts.nth(i)
                produt_images = product.locator("img")
                image_link = produt_images.nth(0).get_attribute('src')

                product_all_links = product.locator('a')
                product_link = product_all_links.nth(0).get_attribute('href')

                product__all_prices = product.locator("div:has-text('₹')")
                product_price = product__all_prices.nth(-1).inner_text()
                product_price = product_price.strip() if product_price else "N/A"

                product_title = produt_images.nth(0).get_attribute('alt')

                if not product_title:
                    continue

                results.append({
                    "category": name,
                    "title": product_title,
                    "price": product_price,
                    "image_link": image_link,
                    "product_link": f"https://www.flipkart.com{product_link}",
                })

        browser.close()


# ---------- ASYNC RUNNER (called from FastAPI) ----------
async def run_all_scraper():
    """Run the sync scrapers in parallel using threads"""
    import concurrent.futures
    
    results = []
    loop = asyncio.get_event_loop()
    
    # Run each scraper in its own thread
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            loop.run_in_executor(executor, Scrape_product, "laptop", results),
            loop.run_in_executor(executor, Scrape_product, "mobile", results),
            loop.run_in_executor(executor, Scrape_product, "tab", results),
        ]
        await asyncio.gather(*futures)
    
    return results


