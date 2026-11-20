import pytest
from playwright.async_api import Page, Browser, async_playwright
from src.entities.browser import browser_launch, browser_close, browser_create_new_page

@pytest.mark.asyncio
async def test_browser_launch( test_context ):
  async with async_playwright() as playwright:
    browser = await browser_launch( 
      ctx = test_context, 
      browser_type = playwright.chromium
    )
    
    await browser.close()

    assert isinstance( browser, Browser )

@pytest.mark.asyncio
async def test_browser_close( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    result = await browser_close( 
      ctx = test_context, 
      browser = browser
    )

    assert result == None

@pytest.mark.asyncio
async def test_browser_create_new_page( test_context ):
  async with async_playwright() as playwright:
    browser = await playwright.chromium.launch()

    result = await browser_create_new_page( 
      ctx = test_context, 
      browser = browser
    )

    assert isinstance( result, Page )