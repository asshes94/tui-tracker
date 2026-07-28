import os

TUI_URL = (
    "https://www.tui.se/h/se/hitta-din-resa?"
    "airports%5B%5D=GOT&"
    "units%5B%5D=G-000000653%3ADESTINATION&"
    "when=08-09-2026&until=&"
    "flexibility=true&monthSearch=false&flexibleDays=7&flexibleMonths=&"
    "noOfAdults=2&noOfChildren=0&childrenAge=&"
    "duration=7115&choiceSearch=true&searchRequestType=ins&"
    "searchType=search&sp=true&multiSelect=true&room=&isVilla=false&"
    "reqType=&sortBy=&fcp=false&semanticSearchType=Default"
)

DESTINATION = "Zakynthos"
DEPARTURE = "Göteborg Landvetter"
DATE_RANGE = "4–8 September 2026"
TRIP_LENGTH = "7 days"
TRAVELERS = 2
MAX_PRICE_SEK = 25_000

EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", EMAIL_USER)

HISTORY_FILE = "history.json"
DEBUG_TEXT_FILE = "debug_page_text.txt"
DEBUG_SCREENSHOT_FILE = "debug_screenshot.png"
