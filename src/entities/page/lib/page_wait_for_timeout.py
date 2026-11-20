from playwright.async_api import Page
from src.app import AppContext

async def page_wait_for_timeout( ctx: AppContext, page: Page, timeout: int = None ):
  timeout_variable = timeout if timeout else ctx.config.timeouts_global["page_timeouts"]["wait_for"]

  ctx.logger.info( f"Waiting for timeout: {timeout_variable}ms" )

  return await page.wait_for_timeout( timeout = timeout_variable )