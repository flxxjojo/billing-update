from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 700, "height": 400})

    # Load local banner.html
    page.goto("http://127.0.0.1:5500/banner.html")

    # Wait for the banner element
    page.wait_for_selector("#banner")

    banner = page.query_selector("#banner")

    # Take screenshot
    banner.screenshot(path="static/billing_banner.png")

    browser.close()