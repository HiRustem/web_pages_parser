import pytest
from playwright.async_api import BrowserType
from src.entities.browser import get_browser_instance

@pytest.mark.asyncio
async def test_get_browser_instance_default( test_context ):
  browser_instance = await get_browser_instance( ctx = test_context )

  assert isinstance( browser_instance, BrowserType )

@pytest.mark.asyncio
async def test_get_browser_instance_firefox( test_context ):
  browser_instance = await get_browser_instance( ctx = test_context )

  assert isinstance( browser_instance, BrowserType )

@pytest.mark.asyncio
async def test_get_browser_instance_chromium( test_context ):
  browser_instance = await get_browser_instance( ctx = test_context )

  assert isinstance( browser_instance, BrowserType )