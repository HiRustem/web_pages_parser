from src.entities.page import page_wait_for_timeout
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_page_wait_for_timeout( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page_wait_for_timeout( 
      ctx = test_context,
      page = page 
    )

    await browser.close()