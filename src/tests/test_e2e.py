import os
import sys

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from vacancy_collector import collect_vacancies

HH_URL = "https://hh.ru"
SEARCH_INPUT = "input[data-qa='search-input']"
VACANCY_ITEM = "a[data-qa='serp-item__title']"
COOKIE_ACCEPT = "[data-qa='cookies-policy-informer-accept']"


@pytest_asyncio.fixture
async def page():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        ctx = await browser.new_context()
        pg = await ctx.new_page()
        yield pg
        await browser.close()


async def _submit_search(page):
    await page.evaluate("""() => {
      const input = document.querySelector('input[data-qa="search-input"]');
      const form = input ? input.closest('form') : null;
      if (form) form.submit();
    }""")


@pytest.mark.asyncio
async def test_navigation_to_hh(page):
    await page.goto(HH_URL, wait_until="domcontentloaded", timeout=60000)
    search = page.locator(SEARCH_INPUT).first
    await search.wait_for(state="visible", timeout=30000)
    assert await search.is_visible()


@pytest.mark.asyncio
async def test_search_flow(page):
    await page.goto(HH_URL, wait_until="domcontentloaded", timeout=60000)
    search = page.locator(SEARCH_INPUT).first
    await search.wait_for(state="visible", timeout=30000)
    await search.fill("frontend")
    await _submit_search(page)
    item = page.locator(VACANCY_ITEM).first
    await item.wait_for(state="visible", timeout=30000)
    assert await item.is_visible()


@pytest.mark.asyncio
async def test_scrape_data_full_page(page):
    """Проверяем, что при пагинации собираются вакансии с нескольких страниц,
    а не только ~20 с первой (lazy loading обработан через переходы по страницам)."""
    await page.goto(HH_URL, wait_until="domcontentloaded", timeout=60000)
    search = page.locator(SEARCH_INPUT).first
    await search.wait_for(state="visible", timeout=30000)
    await search.fill("frontend")
    await _submit_search(page)
    await page.wait_for_selector(VACANCY_ITEM, timeout=30000)

    vacancies = await collect_vacancies(page, "frontend", max_vacancies=40)
    assert len(vacancies) > 20, f"expected >20 vacancies (pagination not handled), got {len(vacancies)}"
    for v in vacancies:
        assert v["title"]
        assert "/vacancy/" in v["link"]
