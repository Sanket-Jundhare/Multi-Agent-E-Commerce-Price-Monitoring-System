from playwright.sync_api import sync_playwright
import re
import time

def get_flipkart_price(product_name: str):
    """
    Get price from Flipkart
    """
    try:
        search_url = f"https://www.flipkart.com/search?q={product_name.replace(' ', '%20')}"
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            page.goto(search_url, timeout=60000, wait_until='networkidle')
            time.sleep(2)
            
            # Try different selectors for Flipkart
            selectors = [
                "div._30jeq3",
                "div._16Jk6d",
                "[class*='price']",
                "div._1vC4OE"
            ]
            
            price = None
            for selector in selectors:
                elements = page.query_selector_all(selector)
                if elements:
                    for element in elements:
                        text = element.inner_text().strip()
                        # Extract numbers
                        numbers = re.findall(r'\d+', text.replace(',', ''))
                        if numbers:
                            price = int(''.join(numbers))
                            if 1000 < price < 200000:
                                break
                if price:
                    break
            
            browser.close()
            
            if price:
                print(f"✅ Flipkart price for {product_name}: ₹{price}")
                return price
            else:
                print(f"❌ No price found on Flipkart for {product_name}")
                return None
                
    except Exception as e:
        print(f"⚠️ Flipkart scraping error for {product_name}: {str(e)}")
        return None