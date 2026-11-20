import os
import sys

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from vacancy_detail_parser import parse_vacancy_page

TEST_VACANCY_URL = "https://kazan.hh.ru/vacancy/135784248"


@pytest_asyncio.fixture
async def page():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        ctx = await browser.new_context()
        pg = await ctx.new_page()
        yield pg
        await browser.close()


@pytest.mark.asyncio
async def test_parse_real_vacancy(page):
    await page.goto(TEST_VACANCY_URL, wait_until="domcontentloaded", timeout=60000)
    await page.wait_for_selector("[data-qa='vacancy-description']", timeout=30000)

    detail = await parse_vacancy_page(page)

    assert detail["title"]
    assert detail["description"]
    assert "/vacancy/" in detail["link"]
    assert isinstance(detail["skills"], list)
    assert isinstance(detail["metro"], list)
    # Salary / work_format may be None (не указаны) — не падаем
    for key in ("company", "city", "experience", "employment", "schedule", "work_hours"):
        assert key in detail
