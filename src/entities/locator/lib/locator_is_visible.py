from playwright.async_api import Locator
from src.app import AppContext

async def locator_is_visible( ctx: AppContext, locator: Locator, timeout: int = None ):
  is_visible = await locator.is_visible( 
    timeout = timeout if timeout else ctx.timeouts_global["locator_timeouts"]["is_visible"]
  )

  if is_visible:
    ctx.logger.info( f"Locator {locator} is visible" )

    return True
  
  ctx.logger.info( f"Locator {locator} is not visible" )

  return False