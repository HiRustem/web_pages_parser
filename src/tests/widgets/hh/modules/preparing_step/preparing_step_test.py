from src.widgets.hh import preparing_step
from playwright.async_api import async_playwright
import pytest

@pytest.mark.asyncio
async def test_preparing_step( test_context ):
  async with async_playwright() as playwright:
    result = await preparing_step(
      ctx = test_context,
      playwright = playwright
    )

  print("result", result)

  assert result["status"] == True