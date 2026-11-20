from src.app import AppContext
from src.entities.page import page_get_locator
from src.entities.locator import locator_get_locator, locator_check_count
from playwright.async_api import Page
from src.shared import normalize_string_number

async def get_total_vacancies_count( ctx: AppContext, page: Page ) -> int:
  search_header = page_get_locator(
    ctx = ctx,
    page = page,
    selector = ctx.config.selectors["vacancies"]["search_header"]
  )

  if not await locator_check_count(
    ctx = ctx,
    locator = search_header
  ):
    ctx.logger.error( "Search header was not found" )

    return 0
  
  search_header_h1 = locator_get_locator(
    ctx = ctx,
    locator = search_header,
    selector_or_locator = ctx.config.selectors["vacancies"]["search_header_h1"]
  )
  
  if not await locator_check_count(
    ctx = ctx,
    locator = search_header_h1
  ):
    ctx.logger.error( "Search header h1 was not found" )

    return 0
  
  search_header_h1_span = locator_get_locator(
    ctx = ctx,
    locator = search_header_h1,
    selector_or_locator = "span"
  )

  if not await locator_check_count(
    ctx = ctx,
    locator = search_header_h1_span
  ):
    ctx.logger.error( "Search header h1 span was not found" )

    return 0
  
  search_header_h1_span_text_content = await search_header_h1_span.text_content()
  
  return normalize_string_number(
    string_number = search_header_h1_span_text_content,
    parse_to_int = True
  )
  
