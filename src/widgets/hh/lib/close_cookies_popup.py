from src.features.close_popup import close_popup
from playwright.async_api import Page
from src.app import AppContext

async def close_cookies_popup( ctx: AppContext, page: Page ) -> bool:
  return await close_popup( ctx = ctx, page = page, selectors = ctx.config.selectors["cookies_popup_accept_buttons"] )