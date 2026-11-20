from src.app import AppContext
from playwright.async_api import Page
from src.entities.page import page_get_locator
from src.entities.locator import locator_check_count, locator_get_locator
from src.shared import parse_string_number_to_int

async def get_pagination_info( ctx: AppContext, page: Page ) -> dict:
  pagination_nav_block = page_get_locator(
    ctx = ctx,
    page = page,
    selector = ctx.config.selectors["pagination"]["pagination_nav_block"]
  )

  if not await locator_check_count(
    ctx = ctx,
    locator = pagination_nav_block
  ):
    ctx.logger.error( "Pagination nav block was not found" )

    return {
      "status": False,
      "pages_total_count": 1
    }

  pagination_links = locator_get_locator(
    ctx = ctx,
    locator = pagination_nav_block,
    selector_or_locator = ctx.config.selectors["pagination"]["pagination_list_link_with_page_number"]
  )

  if not await locator_check_count(
    ctx = ctx,
    locator = pagination_links
  ):
    ctx.logger.error( "Pagination links was not found" )

    return {
      "status": False,
      "pages_total_count": 1
    }
  
  pagination_last_link = pagination_links.last

  pagination_last_link_text = await pagination_last_link.text_content()

  pagination_last_link_text_number = parse_string_number_to_int( pagination_last_link_text )

  ctx.logger.info( f"{pagination_last_link_text_number} pages found" )

  return {
    "status": True,
    "pages_total_count": pagination_last_link_text_number
  }