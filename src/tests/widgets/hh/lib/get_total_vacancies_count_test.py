from playwright.async_api import async_playwright
from src.widgets.hh import get_total_vacancies_count
import pytest

TEST_URL = "https://kazan.hh.ru/search/vacancy?text=frontend&area=88&hhtmFrom=main&hhtmFromLabel=vacancy_search_line"


@pytest.mark.asyncio
async def test_get_total_vacancies_count( test_context ):
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

    result = await get_total_vacancies_count(
      ctx = test_context,
      page = page
    )

    assert result is not 0