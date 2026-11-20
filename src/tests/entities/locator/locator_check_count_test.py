from src.entities.locator import locator_check_count
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_locator_check_count( test_context ):
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

    await page.wait_for_timeout(
      timeout = test_context.config.timeouts["wait_for_page_loading_timeout"]
    )

    form_locator = page.locator(
      selector = test_context.selectors["search_input"]["search_input_form"]
    )

    if await locator_check_count(
      ctx = test_context,
      locator = form_locator
    ):
      test_context.logger.info( "Successfully checked locators count" )
    else:
      test_context.logger.error( "Locator was not found" )

    assert await locator_check_count(
      ctx = test_context,
      locator = form_locator
    ) == True

    