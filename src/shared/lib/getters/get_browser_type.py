from src.app import AppContext
from playwright.async_api import BrowserType, Playwright

async def get_browser_type( ctx: AppContext, playwright: Playwright, browser_type: str ) -> BrowserType:
  if browser_type == "chromium":
    ctx.logger.info( "Returning chromium browser type" )

    return playwright.chromium

  if browser_type == "firefox":
    ctx.logger.info( "Returning firefox browser type" )

    return playwright.firefox
  
  ctx.logger.error( "Unknown browser type. Set 'chromium' or 'firefox'. Returning chromium browser type" )

  return playwright.chromium