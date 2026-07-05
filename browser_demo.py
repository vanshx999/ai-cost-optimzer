import asyncio
from playwright.async_api import async_playwright


async def demo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("Opening page...")
        await page.goto("https://example.com")

        # FIX 1: Typo — 'screnshot' → 'screenshot'
        await page.screenshot(path="screenshot_demo.png")
        print("Screenshot saved: screenshot_demo.png")

        title = await page.title()
        heading = await page.locator("h1").inner_text()

        print(f"Page Title: {title}")
        print(f"Main heading: {heading}")

        # Good practice: close the browser so you don't leave zombie processes
        await browser.close()


async def search_demo():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        print("\n-- Search Demo --")
        await page.goto("https://duckduckgo.com")

        # FIX 2: Close the CSS selector properly — input[name="q"]
        await page.fill('input[name="q"]', "LLM API Pricing comparison 2026")
        await page.press('input[name="q"]', "Enter")

        # FIX 3: Don't look for a <result> tag. Wait for the page to settle instead.
        # DuckDuckGo is heavily JS-driven, so networkidle is more robust than a brittle class.
        await page.wait_for_load_state("networkidle")

        # Try a few selectors since frontends change. DuckDuckGo uses data-testid or article tags.
        results = []
        for selector in ["[data-testid='result']", "article[data-testid='result']", ".result"]:
            try:
                results = await page.locator(selector).all_inner_texts()
                if results:
                    break
            except Exception:
                continue

        print(f"Found {len(results)} results")

        # FIX 4: Don't shadow the outer 'results' list with your loop variable
        for i, result in enumerate(results[:3], 1):
            clean = " ".join(result.split())
            print(f"\nResult {i}: {clean[:200]}...")

        await page.screenshot(path="search_results.png")
        print(f"\nScreenshot saved: search_results.png")

        await browser.close()


if __name__ == "__main__":
    print("=" * 60)
    print("DAY 31: PLAYWRIGHT BROWSER AUTOMATION")
    print("=" * 60)

    asyncio.run(demo())
    asyncio.run(search_demo())

    print("\nDone! Check the screenshots in your project folder")