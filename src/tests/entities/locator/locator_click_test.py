from src.entities.locator import locator_click
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_locator_click( test_context ):
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
      timeout=30000 
    )

    search_submit_form_locator = page.locator( 
      selector = test_context.config.selectors["search_input"]["search_input_form"]
    )

    search_submit_form_submit_button_locator = search_submit_form_locator.locator( 
      selector_or_locator = test_context.config.selectors["search_input"]["search_input_form_submit_button"]
    )

    if await search_submit_form_submit_button_locator.count() == 0:
      test_context.logger.warning( "Form submit button was not found" )
    else:
      await locator_click( 
        ctx = test_context,
        locator = search_submit_form_submit_button_locator
      )

      test_context.logger.warning( "Form submit button was clicked" )

    await browser.close()