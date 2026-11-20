from playwright.async_api import async_playwright, BrowserType
from src.app import AppContext

async def get_browser_instance( ctx: AppContext, browser_name: str = None ) -> BrowserType:
  async with async_playwright() as playwright:
    selected_browser_name = browser_name if browser_name else ctx.config.browser

    if (selected_browser_name == "chromium"):
      ctx.logger.info( "Selected browser - chromium" )

      return playwright.chromium
    
    if (selected_browser_name == "firefox"):
      ctx.logger.info( "Selected browser - firefox" )

      return playwright.firefox

    return None