from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
import os
import pyotp

# Load environment variables from .env
load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
TWOFA_SECRET = os.getenv("TWOFA_SECRET")
COMPANY_NUMBER = os.getenv("COMPANY_NUMBER")  # Default company number, check your invoice
USE_2FA = os.getenv("USE_2FA", "true").lower() == "true"  # Enable or disable 2FA based on environment variable

def apply_stealth(page):
    """Apply stealth mode to avoid detection as an automated script."""
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => false,
        });
        window.navigator.chrome = {
            runtime: {},
        };
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en'],
        });
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3],
        });
    """)

def extract_usage_link(page):
    """Extract the usage link for CSV download."""
    links = page.query_selector_all('a.btn.btn-detail')
    for link in links:
        href = link.get_attribute('href')
        if href and "usage.hetzner.com" in href:
            return href
    return None

def main():
    with sync_playwright() as p:
        # Launch the browser
        browser = p.chromium.launch(headless=True)

        # Create browser context and page
        context = browser.new_context(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        page = context.new_page()
        apply_stealth(page)

        # Log in to the account
        page.goto('https://accounts.hetzner.com/login')
        page.type('input#_username', USERNAME)
        page.type('input#_password', PASSWORD)
        page.click('input#submit-login')
        page.wait_for_load_state('load')

        # Handle 2FA if enabled
        if USE_2FA:
            totp = pyotp.TOTP(TWOFA_SECRET)
            otp = totp.now()
            page.type("input#input-verify-code", otp)
            page.click("input#btn-submit")
            page.wait_for_load_state('load')

        # Navigate to the invoices page
        page.goto('https://accounts.hetzner.com/invoice')

        # Wait for "Details" buttons to load
        page.wait_for_selector('a.btn.btn-detail')

        # Extract the usage link
        usage_link = extract_usage_link(page)
        if not usage_link:
            print("Usage link on usage.hetzner.com not found.")
            return

        print(f"Found usage link: {usage_link}")

        # Generate the CSV download link
        csv_link = f"{usage_link}?csv&cn={COMPANY_NUMBER}"
        print(f"CSV download link: {csv_link}")

        # Download the CSV file using page.request
        response = page.request.get(csv_link)
        if response.status != 200:
            print(f"Error downloading CSV. Status code: {response.status}")
            return

        # Save the downloaded file
        file_path = "invoice.csv"
        with open(file_path, "wb") as f:
            f.write(response.body())
        print(f"CSV file downloaded: {file_path}")

        # Close the browser
        browser.close()

if __name__ == "__main__":
    main()
