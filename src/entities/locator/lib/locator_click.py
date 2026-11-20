from playwright.async_api import Locator
from src.app import AppContext

async def locator_click( ctx: AppContext, locator: Locator, timeout: int = None ):
  return await locator.click( 
    timeout = timeout if timeout else ctx.timeouts_global["locator_timeouts"]["click"]
  )