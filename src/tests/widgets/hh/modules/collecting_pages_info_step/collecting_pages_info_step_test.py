from playwright.async_api import async_playwright
import pytest
from src.widgets.hh import collecting_pages_info_step

@pytest.mark.asyncio
async def test_collecting_pages_info_step( test_context ):
  async with async_playwright() as playwright:
    await collecting_pages_info_step(
      ctx = test_context,
      playwright = playwright,
      previous_step_result = {
        'status': True, 
        'page': {
          'url': 'https://kazan.hh.ru/search/vacancy?hhtmFrom=vacancy_search_list&hhtmFromLabel=chip_filter&text=frontend&search_field=name&search_field=company_name&search_field=description&enable_snippets=true&hhtmSource=vacancy_search_list&hhtmSourceLabel=vacancy_search_list&L_save_area=true'
        }
      }
    )