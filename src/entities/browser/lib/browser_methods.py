from playwright.async_api import Browser, BrowserType
from src.app import AppContext

async def browser_launch( ctx: AppContext, browser_type: BrowserType, headless: bool = True ) -> Browser:
  ctx.logger.info( f"Launching {ctx.config.browser} browser" )

  return await browser_type.launch(
    headless = headless
  )

async def browser_close( ctx: AppContext, browser: Browser ) -> None:
  ctx.logger.info( f"Closing {ctx.config.browser} browser" )

  return await browser.close()

async def browser_create_new_page( ctx: AppContext, browser: Browser ):
  ctx.logger.info( f"Creating {ctx.config.browser} browser new page" )

  return await browser.new_page()
