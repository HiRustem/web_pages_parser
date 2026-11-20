from src.app import AppContext
from playwright.async_api import Page, Error, TimeoutError

async def page_load( ctx: AppContext, page_instance: Page, url, wait_until: str = None, timeout: int = None):
  ctx.logger.info( "Loading page on url: %s", url )

  wait_until_variable = wait_until if wait_until else ctx.config.modes_global["page_loading_wait_until_mode"]
  timeout_variable = timeout if timeout else ctx.config.timeouts_global["page_timeouts"]["loading"]

  try:
    response = await page_instance.goto( 
      url = url, 
      wait_until = wait_until_variable, 
      timeout = timeout_variable 
    )
    
    if response is None:
      ctx.logger.error( "No response from page on url: %s", url )
      return None
    
    if not response.ok:
      ctx.logger.error(
        "HTTP error status: %s while loading page on url: %s",
        response.status,
        url,
      )
      return None
    
    ctx.logger.info( "Loaded page on url: %s", url )

    return response
  
  except TimeoutError:
    ctx.logger.exception( "Timeout while loading page on url: %s. Timeout: %s", url, timeout = timeout_variable )
    return None
  
  except Error:
    ctx.logger.exception( "Playwright error while loading %s", url )
    return None