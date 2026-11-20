from playwright.async_api import Page
from src.app import AppContext

async def page_wait_for_selector( ctx: AppContext, page: Page, selector: str, timeout: int = None, state: str = "visible" ):
  timeout_variable = timeout if timeout else ctx.config.timeouts_global["page_timeouts"]["wait_for_selector"]

  ctx.logger.info( f"Waiting for selector: {selector}" )

  return await page.wait_for_selector(
    selector = selector, 
    timeout = timeout_variable,
    state = state
  )