from playwright.sync_api import sync_playwright
from datetime import datetime

def main():
    print("🚀 TUI Tracker Started")
    print("Time:", datetime.now())

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        url = "https://www.tui.se/"

        print("Opening TUI...")
        page.goto(url, timeout=60000)

        title = page.title()

        print("Page title:")
        print(title)

        browser.close()

    print("✅ Test completed successfully")


if __name__ == "__main__":
    main()
