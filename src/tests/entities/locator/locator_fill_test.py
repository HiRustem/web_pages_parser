from src.entities.locator import locator_fill
from playwright.async_api import async_playwright
import pytest

TEST_QUERY = "query"

@pytest.mark.asyncio
async def test_locator_fill( test_context ):
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

    await locator_fill( 
      ctx = test_context,
      locator = search_locator, 
      value = TEST_QUERY 
    )

    value = await search_locator.input_value()

    assert value == TEST_QUERY

    await browser.close()

