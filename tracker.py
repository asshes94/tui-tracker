from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from config import (
    DATE_RANGE,
    DEBUG_SCREENSHOT_FILE,
    DEBUG_TEXT_FILE,
    DEPARTURE,
    DESTINATION,
    EMAIL_PASSWORD,
    EMAIL_TO,
    EMAIL_USER,
    HISTORY_FILE,
    MAX_PRICE_SEK,
    TRAVELERS,
    TRIP_LENGTH,
    TUI_URL,
)
from history import load_history, save_history
from mailer import send_email


PRICE_PATTERN = re.compile(
    r"(?<!\d)(\d{1,3}(?:[ .\u00a0]\d{3})+|\d{4,6})\s*(?:kr|sek)\b",
    re.IGNORECASE,
)


def normalize_price(raw: str) -> int:
    return int(re.sub(r"\D", "", raw))


def extract_prices(text: str) -> list[int]:
    prices = []
    for match in PRICE_PATTERN.finditer(text):
        price = normalize_price(match.group(1))
        if 1_000 <= price <= 500_000:
            prices.append(price)
    return sorted(set(prices))


def accept_cookies(page: Page) -> None:
    labels = [
        "Acceptera alla",
        "Godkänn alla",
        "Tillåt alla",
        "Accept all",
        "Jag accepterar",
    ]
    for label in labels:
        try:
            button = page.get_by_role("button", name=re.compile(label, re.IGNORECASE))
            if button.count() > 0:
                button.first.click(timeout=2_500)
                page.wait_for_timeout(1_000)
                return
        except Exception:
            continue


def wait_for_results(page: Page) -> None:
    try:
        page.wait_for_load_state("networkidle", timeout=45_000)
    except PlaywrightTimeoutError:
        print("Network did not become fully idle; continuing.")

    page.wait_for_timeout(8_000)

    result_words = re.compile(
        r"(Zakynthos|resultat|hotell|resa|frånpris|pris)",
        re.IGNORECASE,
    )
    try:
        page.locator("body").get_by_text(result_words).first.wait_for(timeout=20_000)
    except Exception:
        print("No obvious result marker found; reading the full page anyway.")


def collect_candidate_blocks(page: Page) -> list[str]:
    blocks: list[str] = []
    price_nodes = page.locator("text=/\\d[\\d .\\u00a0]{2,}\\s*(kr|SEK)/i")
    count = min(price_nodes.count(), 50)

    for index in range(count):
        node = price_nodes.nth(index)
        try:
            text = node.evaluate(
                """element => {
                    let current = element;
                    for (let i = 0; i < 6 && current; i++, current = current.parentElement) {
                        const text = (current.innerText || '').trim();
                        if (text.length >= 60 && text.length <= 1800) return text;
                    }
                    return (element.innerText || '').trim();
                }"""
            )
            cleaned = re.sub(r"\n{3,}", "\n\n", text).strip()
            if cleaned and cleaned not in blocks:
                blocks.append(cleaned)
        except Exception:
            continue

    return blocks


def build_email_body(lowest_price: int, matching_blocks: list[str]) -> str:
    details = "\n\n---\n\n".join(matching_blocks[:8])
    return f"""TUI price alert

Destination: {DESTINATION}
Departure: {DEPARTURE}
Departure dates: {DATE_RANGE}
Trip length: {TRIP_LENGTH}
Travelers: {TRAVELERS}
Maximum price: {MAX_PRICE_SEK:,} SEK
Lowest detected price: {lowest_price:,} SEK

Search link:
{TUI_URL}

Detected result details:
{details if details else "The page contained a qualifying price, but no complete result card could be extracted."}
"""


def main() -> None:
    print("TUI Tracker started:", datetime.now(timezone.utc).isoformat())
    history = load_history(HISTORY_FILE)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            locale="sv-SE",
            timezone_id="Europe/Stockholm",
            viewport={"width": 1440, "height": 1100},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        try:
            print("Opening TUI search page...")
            page.goto(TUI_URL, wait_until="domcontentloaded", timeout=90_000)
            accept_cookies(page)
            wait_for_results(page)

            page_text = page.locator("body").inner_text(timeout=20_000)
            Path(DEBUG_TEXT_FILE).write_text(page_text, encoding="utf-8")
            page.screenshot(path=DEBUG_SCREENSHOT_FILE, full_page=True)

            title = page.title()
            print("Page title:", title)
            print("Page text length:", len(page_text))

            prices = extract_prices(page_text)
            print("Detected prices:", prices[:30])

            candidate_blocks = collect_candidate_blocks(page)
            qualifying_blocks = []
            for block in candidate_blocks:
                block_prices = extract_prices(block)
                if block_prices and min(block_prices) <= MAX_PRICE_SEK:
                    qualifying_blocks.append(block)

            qualifying_prices = [price for price in prices if price <= MAX_PRICE_SEK]
            if not qualifying_prices:
                print(f"No price at or below {MAX_PRICE_SEK:,} SEK was detected.")
                save_history(
                    HISTORY_FILE,
                    {
                        **history,
                        "checked_at": datetime.now(timezone.utc).isoformat(),
                        "last_status": "no_match",
                    },
                )
                return

            lowest_price = min(qualifying_prices)
            result_material = "\n".join(qualifying_blocks) or str(qualifying_prices)
            result_hash = hashlib.sha256(result_material.encode("utf-8")).hexdigest()

            old_price = history.get("last_lowest_price")
            old_hash = history.get("last_result_hash")
            should_notify = old_hash != result_hash or old_price is None or lowest_price < old_price

            print("Lowest qualifying price:", lowest_price)
            print("Notification needed:", should_notify)

            if should_notify:
                body = build_email_body(lowest_price, qualifying_blocks)
                send_email(
                    sender=EMAIL_USER,
                    app_password=EMAIL_PASSWORD,
                    recipient=EMAIL_TO,
                    subject=f"TUI Zakynthos alert: {lowest_price:,} SEK",
                    body=body,
                )
                print("Email sent successfully.")
            else:
                print("Same result already reported; no duplicate email sent.")

            save_history(
                HISTORY_FILE,
                {
                    "checked_at": datetime.now(timezone.utc).isoformat(),
                    "last_status": "match",
                    "last_lowest_price": lowest_price,
                    "last_result_hash": result_hash,
                },
            )
        finally:
            browser.close()


if __name__ == "__main__":
    main()
