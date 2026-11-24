from playwright.sync_api import sync_playwright
import re
import time

def get_amazon_price(product_name: str):
    """
    Get price from Amazon India
    """
    try:
        search_url = f"https://www.amazon.in/s?k={product_name.replace(' ', '+')}"
        
        with sync_playwright() as p:
            # Launch browser in headless mode
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            page = context.new_page()
            
            # Go to Amazon
            page.goto(search_url, timeout=60000, wait_until='networkidle')
            
            # Wait for page to load
            time.sleep(2)
            
            # Try to find price in multiple selectors
            selectors = [
                "span.a-price-whole",
                ".a-price .a-offscreen",
                ".a-text-price span",
                "[data-a-color='price'] span"
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
                            if 1000 < price < 200000:  # Reasonable price range
                                break
                if price:
                    break
            
            browser.close()
            
            if price:
                print(f"✅ Amazon price for {product_name}: ₹{price}")
                return price
            else:
                print(f"❌ No price found on Amazon for {product_name}")
                return None
                
    except Exception as e:
        print(f"⚠️ Amazon scraping error for {product_name}: {str(e)}")
        return None