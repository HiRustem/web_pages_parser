from playwright.async_api import Locator
from src.app import AppContext

async def locator_fill( ctx: AppContext, locator: Locator, value: str, timeout: int = None, no_wait_after: bool = None, force: bool = None ):
  ctx.logger.info( f"Filling locator: {locator} with value: {value}" )

  return await locator.fill( 
    value = value, 
    timeout = timeout if timeout else ctx.config.timeouts_global["locator_timeouts"]["fill"], 
    no_wait_after = no_wait_after, 
    force = force 
  )