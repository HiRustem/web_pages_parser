from src.app import AppContext
from src.entities.browser import browser_launch, browser_create_new_page, browser_close
from src.entities.page import page_load, page_wait_for_selector, page_wait_for_timeout
from src.widgets.hh import close_cookies_popup, close_phone_popup, submit_search_form
from src.shared import get_browser_type
from playwright.async_api import Playwright

async def preparing_step( ctx: AppContext, playwright: Playwright ) -> dict:
  browser = await browser_launch(
    ctx = ctx,
    browser_type = await get_browser_type( 
      ctx = ctx,
      playwright = playwright,
      browser_type = ctx.config.browser
    ),
    headless = False
  )

  page = await browser_create_new_page(
    ctx = ctx,
    browser = browser
  )

  await page_load(
    ctx = ctx,
    page_instance = page,
    url = ctx.config.base_url
  )

  await page_wait_for_selector(
    ctx = ctx,
    page = page,
    selector = ctx.config.selectors["search_input"]["search_input"]
  )

  await page_wait_for_timeout(
    ctx = ctx,
    page = page,
    timeout = ctx.config.timeouts["wait_for_page_loading_timeout"]
  )

  await close_cookies_popup(
    ctx = ctx,
    page = page
  )

  await close_phone_popup(
    ctx = ctx,
    page = page
  )

  input("Prepare page and press Enter key here")

  is_submitted = await submit_search_form(
    ctx = ctx,
    page = page
  )

  await browser_close(
    ctx = ctx,
    browser = browser
  )

  return {
    "status": is_submitted,
    "page": {
      "url": page.url
    }
  }
