from src.entities.locator import locator_get_locator, locator_check_count
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_locator_get_locator( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page.goto( 
      url = test_context.config.base_url,
      wait_until = test_context.config.modes_global["page_loading_wait_until_mode"], 
      timeout = test_context.config.timeouts_global["page_timeouts"]["loading"]
    )

    await page.wait_for_timeout(
      timeout = test_context.config.timeouts["wait_for_page_loading_timeout"]
    )

    search_input_form = page.locator( 
      selector = test_context.config.selectors["search_input"]["search_input_form"]
    )

    form_submit_button_locator = locator_get_locator(
      ctx = test_context,
      locator = search_input_form,
      selector_or_locator = test_context.selectors["search_input"]["search_input_form_submit_button"]
    )

    if not await locator_check_count(
      ctx = test_context,
      locator = form_submit_button_locator
    ):
      test_context.logger.error( "Form submit button locator was not found" )

    assert await form_submit_button_locator.count() is not 0