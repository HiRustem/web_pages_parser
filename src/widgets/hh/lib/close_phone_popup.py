from src.features.close_popup import close_popup
from src.entities.page import page_wait_for_timeout, page_keyboard_press
from playwright.async_api import Page
from src.app import AppContext

async def close_phone_popup( ctx: AppContext, page: Page ) -> bool:
  close_popup_status = await close_popup( 
    ctx = ctx, 
    page = page,
    selectors = ctx.config.selectors["phone_popup_close_buttons"] 
  )

  if close_popup_status:
    ctx.logger.info( "Popup was closed with close_popup function" )

    return True
  
  await page_keyboard_press( 
    ctx = ctx, 
    page = page, 
    key = "Escape" 
  )

  ctx.logger.info( "Escape key was pressed to close phone popup" )

  await page_wait_for_timeout( 
    ctx = ctx, 
    page = page 
  )
  
  return True