from playwright.async_api import async_playwright
from src.widgets.hh import get_pagination_info
import pytest

TEST_URL = "https://kazan.hh.ru/search/vacancy?hhtmFrom=vacancy_search_list&hhtmFromLabel=chip_filter&text=frontend&search_field=name&search_field=company_name&search_field=description&enable_snippets=true&hhtmSource=vacancy_search_list&hhtmSourceLabel=vacancy_search_list&L_save_area=true"

@pytest.mark.asyncio
async def test_get_pagination_info( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    page = await browser.new_page()

    await page.goto( 
      url = TEST_URL,
      wait_until = test_context.config.modes_global["page_loading_wait_until_mode"], 
      timeout = test_context.config.timeouts_global["page_timeouts"]["loading"]
    )

    await page.wait_for_timeout(
      timeout = test_context.config.timeouts["wait_for_page_loading_timeout"]
    )

    result = await get_pagination_info(
      ctx = test_context,
      page = page
    )

    assert result["status"] == True and result["pages_total_count"] >= 1