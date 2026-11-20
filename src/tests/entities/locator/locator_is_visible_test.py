from src.entities.locator import locator_is_visible
from playwright.async_api import async_playwright
import pytest

TEST_SEARCH_INPUT = "input[data-qa='search-input']"

@pytest.mark.asyncio
async def test_locator_is_visible( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page.goto( 
      url = test_context.config.base_url, 
      wait_until = test_context.config.modes_global["page_loading_wait_until_mode"], 
      timeout = test_context.config.timeouts_global["page_timeouts"]["loading"]
    )

    await page.wait_for_selector( 
      selector = test_context.config.selectors["search_input"]["search_input"], 
      timeout = test_context.config.timeouts_global["page_timeouts"]["loading"] 
    )

    search_locator = page.locator( 
      selector = test_context.config.selectors["search_input"]["search_input"]
    ).first

    is_visible = await locator_is_visible( 
      ctx = test_context,
      locator = search_locator 
    )

    assert is_visible == True