from src.app import AppContext
from ...lib.get_total_vacancies_count import get_total_vacancies_count
from ...lib.get_pagination_info import get_pagination_info
from src.entities.browser import browser_launch, browser_create_new_page, browser_close
from src.entities.page import page_load, page_wait_for_timeout
from src.shared import get_browser_type
from playwright.async_api import Playwright

async def collecting_pages_info_step( ctx: AppContext, playwright: Playwright, previous_step_result: dict ) -> dict:
  browser = await browser_launch(
    ctx = ctx,
    browser_type = await get_browser_type( 
      ctx = ctx,
      playwright = playwright,
      browser_type = ctx.config.browser
    ),
  )

  page = await browser_create_new_page(
    ctx = ctx,
    browser = browser
  )

  await page_load(
    ctx = ctx,
    page_instance = page,
    url = previous_step_result["page"]["url"]
  )

  await page_wait_for_timeout(
    ctx = ctx,
    page = page,
    timeout = ctx.config.timeouts["wait_for_page_loading_timeout"]
  )

  vacancies_total_count = await get_total_vacancies_count(
    ctx = ctx,
    page = page
  )

  if vacancies_total_count == 0:
    ctx.logger.error( "Vacancies were not found" )

    return {
      **previous_step_result,
      "status": False,
      "vacancies": {
        "total_count": 0,
      },
      "pagination": {
        "pages_total_count": 1
      }
    }

  ctx.logger.info( f"Vacancies total count: {vacancies_total_count}" )

  pagination_info = await get_pagination_info(
    ctx = ctx,
    page = page,
  )

  if not pagination_info["status"]:
    ctx.logger.error( "Pages were not found" )

    return {
      **previous_step_result,
      "status": False,
      "vacancies": {
        "total_count": 0,
      },
      "pagination": {
        "pages_total_count": 1
      }
    }

  ctx.logger.info( f"Pages total count: {pagination_info["pages_total_count"]}" )

  await browser_close(
    ctx = ctx,
    browser = browser
  )

  return {
    **previous_step_result,
    "vacancies": {
      "total_count": vacancies_total_count,
    },
    "pagination": {
      "pages_total_count": pagination_info["pages_total_count"]
    }
  }