import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 800})
        await page.goto("file:///Users/bhavikdalal/Documents/data warehouse/project/physical_erd_task3b.html")
        await page.wait_for_selector('svg') # Wait for mermaid to render
        await page.screenshot(path="report_charts/physical_erd_task3b_clean.png", full_page=True)
        await browser.close()

asyncio.run(main())
