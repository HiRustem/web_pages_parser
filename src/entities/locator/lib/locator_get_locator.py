from src.app import AppContext
from playwright.async_api import Locator

def locator_get_locator( ctx: AppContext, locator: Locator, selector_or_locator: str | Locator, has_text: str = None, has_not_text: str = None, has: Locator = None ) -> Locator:
  ctx.logger.info( f"Getting locator with selector: {selector_or_locator} with parent: {locator}" )

  return locator.locator( 
    selector_or_locator = selector_or_locator, 
    has_text = has_text, 
    has_not_text = has_not_text, 
    has = has 
  )