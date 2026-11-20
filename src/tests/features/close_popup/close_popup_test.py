from src.features.close_popup import close_popup
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_close_popup( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page.goto( 
      url = test_context.config.base_url,
      wait_until = test_context.config.modes_global["page_loading_wait_until_mode"], 
      timeout = test_context.config.timeouts_global["page_timeouts"]["loading"]
    )

    result = await close_popup( 
      ctx = test_context,
      page = page, 
      selectors = test_context.config.selectors["cookies_popup_accept_buttons"]
    )

    await browser.close()

    assert result == True