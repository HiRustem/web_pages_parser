from src.entities.page import page_load
from playwright.async_api import async_playwright
import pytest


@pytest.mark.asyncio
async def test_page_load( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    loaded_page = await page_load( 
      ctx = test_context,
      page_instance = page, 
      url = test_context.config.base_url
    )

    await browser.close()

    assert loaded_page is not None

