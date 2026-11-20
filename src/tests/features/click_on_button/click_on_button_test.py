from src.features.click_on_button import click_on_button
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_click_on_button( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page.goto( 
      url = test_context.config.base_url,
      wait_until = test_context.config.modes_global["page_loading_wait_until_mode"], 
      timeout = test_context.config.timeouts_global["page_timeouts"]["loading"]
    )

    result = await click_on_button( 
      ctx = test_context,
      page = page, 
      selector = test_context.config.selectors["cookies_popup_accept_buttons"][0]
    )

    await browser.close()

    assert result == True