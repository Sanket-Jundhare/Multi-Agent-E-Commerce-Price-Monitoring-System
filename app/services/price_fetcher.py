import random

def fetch_price(product_name: str) -> dict:
    """
    Mock price fetcher for testing.
    Replace with real scraping logic later.
    """
    # Simulate price between 30k and 90k
    price = random.randint(30000, 90000)
    print(f"📦 Fetched price for {product_name}: ₹{price}")
    
    return {
        "price": price,
        "site": "mock"
    }