from src.app import AppContext
from playwright.async_api import Locator

async def locator_check_count( ctx: AppContext, locator: Locator ) -> bool:
  ctx.logger.info( f"Checking elements count of locator: {locator}" )

  return await locator.count() != 0

