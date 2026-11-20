from src.entities.page import page_wait_for_selector, page_load
from playwright.async_api import async_playwright, ElementHandle
import pytest

@pytest.mark.asyncio
async def test_page_wait_for_selector( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page_load( 
      ctx = test_context,
      page_instance = page, 
      url = test_context.config.base_url 
    )

    element_handle = await page_wait_for_selector( 
      ctx = test_context,
      page = page, 
      selector = test_context.config.selectors["search_input"]["search_input"] 
    )

    await browser.close()

    assert isinstance( element_handle, ElementHandle )