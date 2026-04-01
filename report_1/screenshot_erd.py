import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1600, "height": 1100})
        await page.goto("file:///Users/bhavikdalal/Documents/data warehouse/project/full_erd.html")
        await page.wait_for_timeout(2000)  # Wait for rendering
        await page.screenshot(
            path="/Users/bhavikdalal/Documents/data warehouse/project/report_charts/full_warehouse_erd.png",
            full_page=True
        )
        print("Screenshot saved: report_charts/full_warehouse_erd.png")
        await browser.close()

asyncio.run(main())
