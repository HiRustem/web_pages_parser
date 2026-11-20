from src.entities.page import page_keyboard_press
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_page_keyboard_press( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page_keyboard_press( 
      ctx = test_context,
      page = page, 
      key="Escape" 
    )

    await browser.close()

