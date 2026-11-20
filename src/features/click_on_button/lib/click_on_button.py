from src.entities.page import page_get_locator, page_wait_for_timeout
from src.entities.locator import locator_is_visible, locator_click
from playwright.async_api import Page
from src.app import AppContext

async def click_on_button( ctx: AppContext, page: Page, selector: str, wait_for_timeout: int = None ):
  ctx.logger.info( f"Clicking on button by selector: {selector}" )

  button = page_get_locator( 
    ctx = ctx,
    page = page, 
    selector = selector 
  ).first
  
  if await locator_is_visible( 
    ctx = ctx,
    locator = button 
  ):
    await locator_click(
      ctx = ctx,
      locator = button 
    )
    await page_wait_for_timeout( 
      ctx = ctx,
      page = page, 
      timeout = wait_for_timeout if wait_for_timeout else ctx.config.timeouts_global["page_timeouts"]["wait_for"]
    )

    ctx.logger.info( f"Button by selector: {selector} was clicked" )

    return True
  
  ctx.logger.info( f"Button by selector: {selector} was not clicked" )

  return False