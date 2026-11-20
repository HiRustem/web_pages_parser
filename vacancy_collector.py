import asyncio
import urllib.parse
import re

from vacancy_parser import scrape_vacancies

VACANCY_ITEM = "a[data-qa='serp-item__title']"
PAGE_WAIT_TIMEOUT = 5000
CAPTCHA_SELECTOR = "text=Капча, text=Введите код, [data-qa='captcha']"

# HH ограничивает выдачу постранично — дальше идут пустые/защитные страницы.
MAX_PAGES_HARD_LIMIT = 100

# Ищем текст вида "Найдено 14 358 вакансий" по ВСЕМУ документу через JS.
# ВАЖНО: hh.ru часто рендерит число в отдельном <span> от слов "Найдено"/"вакансий"
# ("Найдено"+"14 358"+"вакансий" — три разных text-узла). Поэтому матчим не по
# отдельным текстовым узлам, а по el.textContent элементов — он склеивает текст
# ВСЕХ потомков. Чтобы не поймать весь <body> (там тоже есть эти слова где-то в
# тексте), берём среди совпадений элемент с минимальной длиной текста — это и
# будет самый "тесный" контейнер, где эти слова стоят рядом.
TOTAL_JS = r"""() => {
  const RE_STRICT = /найдено\s+([\d\s\u00a0\u202f]{1,10})\s*вакан/i;
  const RE_LOOSE = /([\d\s\u00a0\u202f]{2,10})\s*вакан/i;

  function findBest(regex, maxLen) {
    const all = document.querySelectorAll('body *');
    let best = null;
    for (const el of all) {
      const t = el.textContent.replace(/\s+/g, ' ').trim();
      if (!t || t.length > maxLen) continue;
      const m = t.match(regex);
      if (m && (!best || t.length < best.len)) {
        best = { value: m[1], len: t.length };
      }
    }
    return best ? best.value : null;
  }

  return findBest(RE_STRICT, 60) || findBest(RE_LOOSE, 60);
}
"""


def _clean_number(raw: str):
    """Убирает ВСЕ виды пробелов (обычный, \u00a0, \u202f и т.п.) и парсит int."""
    if not raw:
        return None
    digits_only = re.sub(r"\D", "", raw)
    if not digits_only:
        return None
    return int(digits_only)


async def get_total_vacancies(page):
    """Достаёт общее число вакансий со страницы результатов поиска."""
    try:
        raw = await page.evaluate(TOTAL_JS)
    except Exception:
        raw = None
    return _clean_number(raw)


async def detect_captcha(page):
    """Проверяет, показывает ли ТЕКУЩАЯ (уже загруженная) страница капчу."""
    for selector in CAPTCHA_SELECTOR.split(", "):
        try:
            el = page.locator(selector).first
            if await el.is_visible(timeout=2000):
                return True
        except Exception:
            continue
    return False


async def wait_for_vacancy_items(page, timeout=PAGE_WAIT_TIMEOUT):
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        count = await page.locator(VACANCY_ITEM).count()
        if count > 0:
            return True
        await page.wait_for_timeout(500)
    return False


async def _process_page(page, url, timeout_sec=15):
    """Загружает страницу и проверяет её состояние. Возвращает строковый статус:
    "ok" / "empty" / "captcha". Внешний asyncio.wait_for гарантирует, что весь
    блок (goto + detect_captcha + wait_for_vacancy_items) не будет висеть дольше
    timeout_sec — это предохранитель, не зависящий от внутренних таймаутов."""
    await page.goto(url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
    if await detect_captcha(page):
        return "captcha"
    loaded = await wait_for_vacancy_items(page, timeout=PAGE_WAIT_TIMEOUT)
    return "ok" if loaded else "empty"


# ВАЖНО: это осознанно БЕЛЫЙ, а не чёрный список. HH может в любой момент
# добавить новый служебный/аналитический query-параметр (как suggestId,
# hhtmFrom), и чёрный список тогда снова пропустит мусор в пагинацию.
# Белый список — осознанная защита на будущее: переносятся только реальные
# фильтры поиска.
ALLOWED_FILTER_PARAMS = {
    "area", "salary", "currency", "experience", "schedule",
    "employment", "professional_role", "metro", "search_period",
    "order_by", "only_with_salary", "no_magic",
}


def extract_search_params(url: str) -> dict:
    """Извлекает фильтры поиска (напр. area=NN — город) из URL первой страницы
    результатов, чтобы сохранить их при построении URL пагинации.
    Пропускает только ключи из ALLOWED_FILTER_PARAMS — служебные/аналитические
    параметры (suggestId, hhtmFrom, hhtmFromLabel и т.п.) не переносятся."""
    parsed = urllib.parse.urlparse(url)
    params = urllib.parse.parse_qs(parsed.query)
    return {k: v[0] for k, v in params.items() if k in ALLOWED_FILTER_PARAMS}


def build_search_url(query: str, page_num: int, extra_params=None) -> str:
    """Всегда строит URL пагинации от корректной базы /search/vacancy,
    а не от page.url (который может оказаться главной страницей).
    extra_params — доп. query-параметры (например {"area": "88"}), которые
    сохраняют фильтр города с первой страницы на всех остальных."""
    base = f"https://hh.ru/search/vacancy?text={urllib.parse.quote(query)}"
    if extra_params:
        base += "&" + urllib.parse.urlencode(extra_params)
    if page_num > 0:
        base += f"&page={page_num}"
    return base


async def collect_vacancies(page, query, max_vacancies=None, extra_params=None):
    """
    query — исходный текст запроса, нужен, чтобы всегда строить корректный
    URL пагинации независимо от того, куда реально указывает page.url.
    extra_params — query-параметры первой страницы (напр. area), чтобы
    фильтр города сохранялся при переходе по страницам.
    """
    seen = {}
    page_num = 0

    while True:
        if max_vacancies is not None and len(seen) >= max_vacancies:
            print(f"Достигнуто целевое количество ({max_vacancies}).", flush=True)
            break

        if page_num >= MAX_PAGES_HARD_LIMIT:
            print("Достигнут предел выдачи hh.ru (~100 страниц), завершаю сбор.", flush=True)
            break

        if page_num > 0:
            url = build_search_url(query, page_num, extra_params=extra_params)
            print(f"Перехожу на страницу {page_num + 1}: {url}", flush=True)
            # Внешний предохранитель: весь блок обработки страницы ограничен 15 сек,
            # независимо от того, где именно внутри происходит зависание.
            try:
                status = await asyncio.wait_for(_process_page(page, url), timeout=15)
            except asyncio.TimeoutError:
                print(f"Страница {page_num + 1} зависла (>15 сек), завершаю сбор.", flush=True)
                break
            except Exception as e:
                print(f"Не удалось загрузить страницу {page_num + 1} ({str(e)[:150]}), завершаю сбор.", flush=True)
                break
            if status == "captcha":
                print("Обнаружена капча, завершаю сбор.", flush=True)
                break
            if status == "empty":
                print(f"Страница {page_num + 1} пуста, завершаю сбор.", flush=True)
                break

        loaded = await wait_for_vacancy_items(page, timeout=PAGE_WAIT_TIMEOUT)
        if not loaded:
            # Пустая страница на первой итерации тоже может значить капчу — перепроверим.
            if await detect_captcha(page):
                print("Обнаружена капча, завершаю сбор.", flush=True)
            else:
                print(f"Страница {page_num + 1} пуста, завершаю сбор.", flush=True)
            break

        vacancies = await scrape_vacancies(page)
        added = 0
        for v in vacancies:
            if max_vacancies is not None and len(seen) >= max_vacancies:
                break
            link = v["link"].split("?")[0]
            if link not in seen:
                seen[link] = {"title": v["title"], "link": link}
                added += 1
        print(f"Страница {page_num + 1}: найдено {len(vacancies)}, новых {added} (всего {len(seen)}).", flush=True)

        if added == 0 and page_num > 0:
            print("Новых вакансий нет, завершаю сбор.", flush=True)
            break

        if max_vacancies is not None and len(seen) >= max_vacancies:
            print(f"Достигнуто целевое количество ({max_vacancies}).", flush=True)
            break

        page_num += 1
        await asyncio.sleep(1.5)

    return list(seen.values())
