from src.widgets.hh import close_cookies_popup
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_close_cookies_popup( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page.goto( 
      url = test_context.config.base_url,
      wait_until = test_context.config.modes_global["page_loading_wait_until_mode"], 
      timeout = test_context.config.timeouts_global["page_timeouts"]["loading"]
    )

    result = await close_cookies_popup( 
      ctx = test_context,
      page = page
    )

    await browser.close()

    assert result == True