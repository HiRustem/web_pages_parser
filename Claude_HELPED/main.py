import argparse
import asyncio
import json
import sys
import urllib.parse

from playwright.async_api import async_playwright

from details_writer import write_details
from vacancy_collector import collect_vacancies, get_total_vacancies, build_search_url
from vacancy_detail_parser import parse_vacancy_page
from vacancy_writer import summary_message, write_vacancies

HH_URL = "https://hh.ru"
SEARCH_INPUT = "input[data-qa='search-input']"
VACANCY_ITEM = "a[data-qa='serp-item__title']"
MODAL_CLOSE = "[data-qa='bloko-modal-close']"
COOKIE_ACCEPT = "[data-qa='cookies-policy-informer-accept']"
DETAIL_LOAD_TIMEOUT = 25000

PHONE_POPUP_BUTTONS = [
    "button:has-text('Продолжить без номера')",
    "text=Позже",
    "button:has-text('Продолжить без телефона')",
    "button:has-text('Не сейчас')",
]

if sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


async def close_phone_popup(page):
    for selector in PHONE_POPUP_BUTTONS:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=1500):
                await btn.click(timeout=3000)
                await page.wait_for_timeout(800)
                return True
        except Exception:
            continue
    try:
        close_btn = page.locator(MODAL_CLOSE).first
        if await close_btn.is_visible(timeout=1500):
            await close_btn.click(timeout=3000)
            await page.wait_for_timeout(800)
            return True
    except Exception:
        pass
    try:
        await page.keyboard.press("Escape")
        await page.wait_for_timeout(500)
        return True
    except Exception:
        pass
    return False


async def close_cookie_popup(page):
    try:
        btn = page.locator(COOKIE_ACCEPT).first
        if await btn.is_visible(timeout=2000):
            await btn.click(timeout=3000)
            await page.wait_for_timeout(500)
            return True
    except Exception:
        pass
    for selector in ["button:has-text('Принять')", "button:has-text('Ок')", "text=Принимаю"]:
        try:
            btn = page.locator(selector).first
            if await btn.is_visible(timeout=1000):
                await btn.click(timeout=3000)
                await page.wait_for_timeout(500)
                return True
        except Exception:
            continue
    return False


async def submit_search_form(page):
    try:
        result = await page.evaluate("""() => {
          const input = document.querySelector('input[data-qa="search-input"]');
          if (!input) return false;
          const form = input.closest('form');
          if (!form) return false;
          form.submit();
          return true;
        }""")
        return result
    except Exception:
        return False


async def parse_single_vacancy(page, link):
    try:
        await page.goto(link, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector("[data-qa='vacancy-description']", timeout=DETAIL_LOAD_TIMEOUT)
        detail = await parse_vacancy_page(page)
        detail["link"] = link.split("?")[0]
        return detail
    except Exception as e:
        return {"link": link, "error": str(e)[:200]}


async def parse_details(page, vacancies, limit, search_url):
    all_details = []

    for i, vac in enumerate(vacancies[:limit]):
        link = vac.get("link")
        if not link:
            all_details.append({"link": None, "error": "no link"})
            continue

        print(f"Парсинг {i + 1}/{limit}: {link}", flush=True)
        result = await parse_single_vacancy(page, link)
        all_details.append(result)

        # Возврат на страницу поиска нужен только чтобы браузер не "провис" на
        # карточке вакансии — сам парсинг уже сделан. Если тут капча/таймаут,
        # не роняем весь цикл: следующая итерация просто перейдёт по прямой
        # ссылке вакансии (parse_single_vacancy делает page.goto сама).
        try:
            await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector(VACANCY_ITEM, timeout=15000)
        except Exception as e:
            print(f"Не удалось вернуться на страницу поиска ({str(e)[:100]}), продолжаю.", flush=True)
        await asyncio.sleep(1)

    return all_details


def _read_int_or_none(prompt):
    """Enter -> None (значит 'все'). Иначе парсит целое число."""
    try:
        raw = input(prompt).strip()
    except EOFError:
        return None
    if not raw:
        return None
    try:
        return int(raw)
    except ValueError:
        print("Не понял число, беру 'все'.")
        return None


async def run(query=None, keep_open=True, detail_count_arg=None):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        await page.goto(HH_URL, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_selector(SEARCH_INPUT, timeout=30000)
        await close_cookie_popup(page)
        await close_phone_popup(page)

        if query is None:
            query = input("Введите название вакансии: ")

        search = page.locator(SEARCH_INPUT).first
        await search.fill(query)
        await page.wait_for_timeout(500)

        submitted = await submit_search_form(page)
        if not submitted:
            await page.goto(build_search_url(query, 0), wait_until="domcontentloaded", timeout=60000)

        # Ждём появления карточек результатов, чтобы счётчик точно успел отрисоваться.
        await page.wait_for_selector(VACANCY_ITEM, timeout=30000)

        total = await get_total_vacancies(page)
        if total is not None:
            print(f"Найдено {total:,} вакансий".replace(",", " "))
        else:
            print("Не удалось определить общее число вакансий, продолжаю сбор.")

        max_vacancies = _read_int_or_none("Сколько скачать? (Enter = все): ")

        vacancies = await collect_vacancies(page, query, max_vacancies=max_vacancies)

        try:
            txt_path, json_path = write_vacancies(query, vacancies)
        except ValueError as e:
            print(f"Ошибка обработки данных: {e}")
            if keep_open:
                while browser.is_connected():
                    await asyncio.sleep(1)
            return

        print(summary_message(len(vacancies), query))
        if txt_path and json_path:
            print(f"Файл: {txt_path}")

        if not vacancies:
            if keep_open:
                print("Браузер оставлен открытым. Закройте его вручную.")
                while browser.is_connected():
                    await asyncio.sleep(1)
            return

        search_url = build_search_url(query, 0)

        if detail_count_arg is None:
            detail_count = _read_int_or_none(
                f"Скачано {len(vacancies)} вакансий. Сколько распарсить текст+навыки? (Enter = все, 0 = пропустить): "
            )
            detail_count = len(vacancies) if detail_count is None else detail_count
        else:
            detail_count = detail_count_arg

        detail_count = max(0, min(detail_count, len(vacancies)))

        if detail_count > 0:
            details = await parse_details(page, vacancies, detail_count, search_url)
            d_json, d_md = write_details(query, details)
            parsed_ok = sum(1 for d in details if "error" not in d)
            print(f"Спарсили {parsed_ok} вакансий. Файл сформирован: {d_json}")
        else:
            print("Парсинг деталей пропущен.")

        if keep_open:
            print("Браузер оставлен открытым. Закройте его вручную.")
            while browser.is_connected():
                await asyncio.sleep(1)


async def run_details_only(input_json, detail_count, keep_open=False):
    with open(input_json, encoding="utf-8") as f:
        data = json.load(f)
    vacancies = data["vacancies"]
    query = data["query"]
    detail_count = max(0, min(detail_count or len(vacancies), len(vacancies)))
    if detail_count <= 0:
        print("Парсинг деталей пропущен.")
        return

    search_url = build_search_url(query, 0)

    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()
        details = await parse_details(page, vacancies, detail_count, search_url)
        d_json, d_md = write_details(query, details)
        parsed_ok = sum(1 for d in details if "error" not in d)
        print(f"Спарсили {parsed_ok} вакансий. Файл сформирован: {d_json}")
        if keep_open:
            print("Браузер оставлен открытым. Закройте его вручную.")
            while browser.is_connected():
                await asyncio.sleep(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HH vacancy search agent")
    parser.add_argument("--query", help="vacancy name (skip interactive prompt)")
    parser.add_argument("--close", action="store_true", help="close browser after finishing (for tests)")
    parser.add_argument("--detail-count", type=int, help="number of vacancies to parse details from")
    parser.add_argument("--input", help="path to vacancies JSON for details-only mode")
    args = parser.parse_args()

    if args.input:
        asyncio.run(run_details_only(args.input, args.detail_count, keep_open=not args.close))
    else:
        asyncio.run(run(query=args.query, keep_open=not args.close, detail_count_arg=args.detail_count))
