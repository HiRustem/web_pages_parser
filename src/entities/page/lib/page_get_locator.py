from playwright.async_api import Locator, Page
from src.app import AppContext

def page_get_locator( ctx: AppContext, page: Page, selector: str, has_text: str = None, has_not_text: str = None, has: Locator = None ):
  ctx.logger.info( f"Getting locator with selector: {selector} on page: {page}" )

  return page.locator( 
    selector = selector, 
    has_text = has_text, 
    has_not_text = has_not_text, 
    has = has 
  )