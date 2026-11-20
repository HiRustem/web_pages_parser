from src.entities.locator import locator_get_locator, locator_click, locator_check_count
from src.entities.page import page_get_locator
from src.app import AppContext
from playwright.async_api import Page

async def submit_search_form( ctx: AppContext, page: Page ) -> bool:
  form_locator = page_get_locator(
    ctx = ctx,
    page = page,
    selector = ctx.selectors["search_input"]["search_input_form"]
  )

  if not await locator_check_count(
    ctx = ctx,
    locator = form_locator
  ):
    ctx.logger.error( "Search input form was not found" )

    return False

  form_submit_button_locator = locator_get_locator(
    ctx = ctx,
    locator = form_locator,
    selector_or_locator = ctx.selectors["search_input"]["search_input_form_submit_button"]
  )

  if not await locator_check_count(
    ctx = ctx,
    locator = form_submit_button_locator
  ):
    ctx.logger.error( "Search input form submit button was not found" )

    return False

  await locator_click( 
    ctx = ctx, 
    locator = form_submit_button_locator 
  )

  ctx.logger.info( "Search input form submit button was clicked" )

  return True