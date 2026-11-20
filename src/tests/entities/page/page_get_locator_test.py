from src.entities.page import page_load, page_get_locator
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_page_get_locator( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page_load( 
      ctx = test_context,
      page_instance = page, 
      url = test_context.config.base_url 
    )

    await page.wait_for_timeout(
      timeout = test_context.config.timeouts["wait_for_page_loading_timeout"]
    )

    locator = page_get_locator( 
      ctx = test_context,
      page = page, 
      selector = test_context.config.selectors["search_input"]["search_input"]
    )

    if await locator.count() == 0:
      test_context.logger.error( "Locator was not found" )

    assert await locator.count() is not 0