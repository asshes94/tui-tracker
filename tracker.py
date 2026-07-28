from playwright.sync_api import sync_playwright
from datetime import datetime

TUI_URL = "https://www.tui.se/h/se/hitta-din-resa?airports%5B%5D=GOT&units%5B%5D=G-000000653%3ADESTINATION&when=08-09-2026&until=&flexibility=true&monthSearch=false&flexibleDays=7&flexibleMonths=&noOfAdults=2&noOfChildren=0&childrenAge=&duration=7115&choiceSearch=true&searchRequestType=ins&searchType=search&sp=true&multiSelect=true&room=&isVilla=false&reqType=&sortBy=&fcp=false&semanticSearchType=Default"

def main():

    print("🚀 TUI Search Started")
    print(datetime.now())

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print("Opening TUI results page...")
        page.goto(TUI_URL, timeout=90000)

        page.wait_for_timeout(10000)

        title = page.title()

        print("Page title:")
        print(title)

        text = page.locator("body").inner_text()

        print("First 1000 characters:")
        print(text[:1000])

        browser.close()

    print("✅ Finished")


if __name__ == "__main__":
    main()
