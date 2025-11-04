from playwright.async_api import async_playwright
import asyncio
import time


# ---------- ASYNC SCRAPER ----------
async def Scrape_product(name, results):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=5)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for page_num in range(1, 10):
            print(f"\n  Scraping {name} | Page {page_num}")
            await page.goto(
                f"https://www.flipkart.com/search?q={name}&otracker=search&page={page_num}",
                wait_until="domcontentloaded"
            )

            last_height = await page.evaluate("document.body.scrollHeight")
            while True:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(1)
                new_height = await page.evaluate("document.body.scrollHeight")
                if new_height == last_height:
                    break
                last_height = new_height

            PageProducts = page.locator("div._75nlfW")
            count = await PageProducts.count()

            for i in range(count):
                product = PageProducts.nth(i)
                produt_images = product.locator("img")
                image_link = await produt_images.nth(0).get_attribute('src')

                product_all_links = product.locator('a')
                product_link = await product_all_links.nth(0).get_attribute('href')

                product__all_prices = product.locator("div:has-text('₹')")
                product_price = await product__all_prices.nth(-1).inner_text()
                product_price = product_price.strip() if product_price else "N/A"

                product_title = await produt_images.nth(0).get_attribute('alt')

                if not product_title:
                    continue

                results.append({
                    "category": name,
                    "title": product_title,
                    "price": product_price,
                    "image_link": image_link,
                    "product_link": f"https://www.flipkart.com{product_link}",
                })

        await browser.close()


# ---------- ASYNC RUNNER ----------
async def run_all_scraper():
    results = []
    tasks = [
        Scrape_product("laptops", results),
        Scrape_product("mobiles", results),
        Scrape_product("tabs", results),
    ]
    await asyncio.gather(*tasks)
    return results  

