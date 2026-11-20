from playwright.async_api import Page
from src.app import AppContext

async def page_keyboard_press( ctx: AppContext, page: Page, key: str, delay: float = None ):
  ctx.logger.info( f"Pressing keyboard with key: {key}" )

  return await page.keyboard.press( 
    key = key, 
    delay = delay
  )