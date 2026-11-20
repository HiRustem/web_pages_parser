import pytest
from playwright.async_api import Page, Browser, async_playwright
from src.shared import get_browser_type

@pytest.mark.asyncio
async def test_get_browser_type_default( test_context ):
  async with async_playwright() as playwright:

    result = await get_browser_type(
      ctx = test_context,
      playwright = playwright,
      browser_type = "unknown",
    )

    assert result == playwright.chromium

@pytest.mark.asyncio
async def test_get_browser_type_chromium( test_context ):
  async with async_playwright() as playwright:

    result = await get_browser_type(
      ctx = test_context,
      playwright = playwright,
      browser_type = "chromium",
    )

    assert result == playwright.chromium

@pytest.mark.asyncio
async def test_get_browser_type_firefox( test_context ):
  async with async_playwright() as playwright:

    result = await get_browser_type(
      ctx = test_context,
      playwright = playwright,
      browser_type = "firefox",
    )

    assert result == playwright.firefox