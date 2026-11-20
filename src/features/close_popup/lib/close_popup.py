from src.entities.page import page_get_locator, page_wait_for_timeout
from src.entities.locator import locator_click, locator_is_visible
from src.app import AppContext
from playwright.async_api import Page

async def close_popup( ctx: AppContext, page: Page, selectors: list[str] ) -> bool:
  ctx.logger.info( f"Closing popup" )

  for selector in selectors:
    cookies_popup_button = page_get_locator( 
      ctx = ctx,
      page = page, 
      selector = selector 
    ).first
  
    if await locator_is_visible( 
      ctx = ctx,
      locator = cookies_popup_button 
    ):
      await locator_click( 
        ctx = ctx,
        locator = cookies_popup_button 
      )
      
      await page_wait_for_timeout( 
        ctx = ctx,
        page = page
      )

      ctx.logger.info( f"Popup found with selector {selector} was closed" )

      return True
    
    continue

  ctx.logger.info( f"Popup was not found" )

  return False