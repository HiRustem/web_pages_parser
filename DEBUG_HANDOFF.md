# DEBUG HANDOFF: Финальное состояние HH-скрапера (ПРОЕКТ ЗАКРЫТ)

> **Статус: ✅ проект завершён, скрипт работает корректно.** Документ содержит финальное состояние: статус, решённые ошибки и риски, актуальный код всех файлов, историю попыток. Пригоден как референс или для передачи модели при будущей доработке.

---

## 1. Контекст проекта

- **Назначение:** Python-скрипт собирает вакансии с hh.ru: поиск по названию → выбор региона → сбор списка (название+ссылка) → сохранение в `Vac/` (TXT+JSON) → опциональный парсинг деталей в `Details/`.
- **Стек:** Python 3.12, Playwright (async), браузер Firefox (НЕ headless), pytest для тестов.
- **Ключевое архитектурное решение:** флоу детерминированный, **LLM в рантайме не используется** (раньше LLM давал неверные селекторы и ложные сообщения об успехе — убран).
- **Рабочая папка:** `C:\Users\Roman\Desktop\AI_Agents\testing\Python_AI_Agent\`
- **Проблема региональности:** HH перенаправляет на региональный домен, напр. `kazan.hh.ru`. Ссылки вакансий вида `https://kazan.hh.ru/vacancy/...`. `page.goto` следует за редиректом автоматически, ссылки берутся из уже отрендеренной страницы.

### Рабочее поведение (подтверждено прогоном)
```
Введите название вакансии: Руководитель колл центра
Найдено 60 вакансий
Собирать по текущему городу или по всей России? (город / вся): город
Сколько скачать? (Enter = все):
Страница 1: найдено 50, новых 50 (всего 50).
Страница 2: найдено 10, новых 10 (всего 60).
Страница 3: пуста, завершаю сбор.        ← корректная остановка за пределами выдачи
Собрано 60 вакансий по названию «...». Файл сформирован и загружен.
```

---

## 2. Требуемый UX (достигнут)

1. Открывается окно браузера (Firefox).
2. Браузер переходит на главную страницу hh.ru.
3. В терминале: «Введите название вакансии:».
4. Пользователь вводит название, поиск отправляется.
5. Показывается **общее число вакансий** (формат «Найдено 60 вакансий» / «Найдено 14 358 вакансий», число корректное).
6. Запрос: «Собирать по текущему городу или по всей России? (город / вся)».
7. Запрос: «Сколько скачать? (Enter = все)».
8. Скрипт перебирает страницы результатов (`search/vacancy?text=...&page=N`, с сохранением фильтра города), пока не наберёт лимит или не упрётся в конец/капчу/лимит 100 страниц.
9. Сохранение в `Vac/` (TXT + JSON), вывод «Собрано N вакансий по названию «...». Файл сформирован и загружен.»
10. **В UI нет упоминания «страниц»** — только «вакансии».

---

## 3. Статус

- ✅ **8 файлов из `Claude_HELPED/` скопированы** в `Python_AI_Agent/`.
- ✅ **Офлайн-тесты:** `pytest tests/test_writer.py` → **8/8 PASSED**.
- ✅ **Синтаксис:** все модули компилируются (ast.parse OK).
- ✅ **Интерактивная проверка:** ручной прогон («Руководитель колл центра», город) — скрипт отработал корректно, остановился на пустой странице за пределами выдачи, зависаний нет.
- ✅ **Проект закрыт.**

---

## 4. Решённые ошибки и риски

### Ошибки (все исправлены)

| # | Проблема | Решение |
|---|---|---|
| 1 | Счётчик 14 вместо 14358 (неразрывный пробел `\u00a0` резал число) | `_clean_number` через `re.sub(r"\D", "", raw)` |
| 2 | Хрупкий селектор `text=Найдено` | JS `TOTAL_JS`: обход `body *`, матч по `el.textContent`, выбор элемента с минимальной длиной |
| 3 | KeyError `{page}` при fallback поиска | Удалён `SEARCH_URL`, добавлен `build_search_url(query, page_num, extra_params=None)` |
| 4 | `base_url = page.url` мог быть главной страницей (`kazan.hh.ru/?page=1`) | URL пагинации строится от `/search/vacancy` с нуля по `query` |
| 5 | Капча проверялась ДО навигации | `detect_captcha` вызывается ПОСЛЕ `goto`; перепроверка на «пустой» странице |
| 6 | `run_details_only` — NameError (`page`/`search_url` не определены) | Создаётся `page`, `search_url` через `build_search_url(query, 0)` |
| 7 | E2E-тест сломан (`max_pages`) | `collect_vacancies(page, "frontend", max_vacancies=40)` |
| 8 | `wait_for_results` — пустышка | Удалена |
| 9 | UX с «страницами» | «Найдено N вакансий» + выбор региона + `MAX_PAGES_HARD_LIMIT = 100` |

### Риски (все закрыты)

| Риск | Статус |
|---|---|
| **A.** TreeWalker по text-узлам не склеивал «Найдено»/«14 358»/«вакансий» из разных `<span>` | ✅ матч по `el.textContent` (текст всех потомков) |
| **B.** Падение всего цикла деталей из-за капчи на возврате к `search_url` | ✅ `try/except` вокруг возврата, цикл продолжается |
| **C.** Региональный редирект `hh.ru → kazan.hh.ru` | ✅ `page.goto` следует за редиректом |
| **D.** Служебные query-параметры (`suggestId`, `hhtmFrom`, `hhtmFromLabel`) попадали в URL пагинации → HH мог срабатывать анти-бот | ✅ `ALLOWED_FILTER_PARAMS` — осознанно БЕЛЫЙ список фильтров |
| **E.** Зависание на странице за пределами выдачи (минуты тишины) | ✅ внешний `asyncio.wait_for(_process_page(...), timeout=15)` + `print` URL каждого перехода |
| **F.** Нативные диалоги Firefox (alert/confirm/prompt) блокируют event loop | ✅ `page.on("dialog", ...)` логирует и закрывает через `dismiss()` |

---

## 5. Ключевые решения в финальном коде

### `ALLOWED_FILTER_PARAMS` — белый список (vacancy_collector.py:102-106)
```python
ALLOWED_FILTER_PARAMS = {
    "area", "salary", "currency", "experience", "schedule",
    "employment", "professional_role", "metro", "search_period",
    "order_by", "only_with_salary", "no_magic",
}
```
**Почему белый, а не чёрный:** HH может в любой момент добавить новый служебный/аналитический параметр (как `suggestId`), и чёрный список снова пропустит мусор в пагинацию. Белый список переносит только реальные фильтры.

### `_process_page` + `asyncio.wait_for` (vacancy_collector.py:85-94, 156-169)
```python
async def _process_page(page, url, timeout_sec=15):
    await page.goto(url, wait_until="domcontentloaded", timeout=timeout_sec * 1000)
    if await detect_captcha(page):
        return "captcha"
    loaded = await wait_for_vacancy_items(page, timeout=PAGE_WAIT_TIMEOUT)
    return "ok" if loaded else "empty"

# в collect_vacancies:
try:
    status = await asyncio.wait_for(_process_page(page, url), timeout=15)
except asyncio.TimeoutError:
    print("Страница N зависла (>15 сек), завершаю сбор."); break
...
```
Внешний `wait_for` гарантирует завершение за 15 сек независимо от того, где внутри зависание (не зависит от внутренних таймаутов).

### Выбор региона (main.py:190-211)
`extract_search_params(page.url)` извлекает фильтры первой страницы (город `area=NN`). Запрос «город / вся»: при «вся» — переход на URL без `area`, `search_params = {}`. Фильтр города сохраняется на всех страницах пагинации через `extra_params`.

---

## 6. Полный код всех файлов (ФИНАЛЬНЫЕ версии)

### `main.py`
```python
import argparse
import asyncio
import json
import sys
import urllib.parse

from playwright.async_api import async_playwright

from details_writer import write_details
from vacancy_collector import collect_vacancies, get_total_vacancies, build_search_url, extract_search_params
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


def _read_choice(prompt):
    """Читает ответ город/вся. Enter -> 'город' (по умолчанию)."""
    try:
        raw = input(prompt).strip().lower()
    except EOFError:
        return "город"
    if not raw:
        return "город"
    return "вся" if raw in ("вся", "все", "россия", "вся россия", "russia", "all") else "город"


async def run(query=None, keep_open=True, detail_count_arg=None):
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=False)
        page = await browser.new_page()

        # Диагностика нативных диалогов Firefox (alert/confirm/prompt),
        # которые могут блокировать event loop и "подвешивать" скрипт.
        page.on("dialog", lambda dialog: (
            print(f"Обнаружен диалог браузера: {dialog.type} — {dialog.message[:100]}", flush=True),
            asyncio.create_task(dialog.dismiss())
        ))

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

        # URL уже финальный после HH-редиректов — извлекаем фильтры (в т.ч. город area=NN).
        search_params = extract_search_params(page.url)

        total = await get_total_vacancies(page)
        if total is not None:
            print(f"Найдено {total:,} вакансий".replace(",", " "))
        else:
            print("Не удалось определить общее число вакансий, продолжаю сбор.")

        # Выбор региона: оставить текущий город или собирать по всей России.
        region = _read_choice("Собирать по текущему городу или по всей России? (город / вся): ")
        if region == "вся":
            await page.goto(build_search_url(query, 0), wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector(VACANCY_ITEM, timeout=30000)
            search_params = {}
            total = await get_total_vacancies(page)
            if total is not None:
                print(f"По всей России найдено {total:,} вакансий".replace(",", " "))

        max_vacancies = _read_int_or_none("Сколько скачать? (Enter = все): ")

        vacancies = await collect_vacancies(page, query, max_vacancies=max_vacancies, extra_params=search_params)

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

        search_url = build_search_url(query, 0, extra_params=search_params)
        print(f"[DEBUG] search_url для возврата в parse_details: {search_url}", flush=True)

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

        page.on("dialog", lambda dialog: (
            print(f"Обнаружен диалог браузера: {dialog.type} — {dialog.message[:100]}", flush=True),
            asyncio.create_task(dialog.dismiss())
        ))

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
```

### `vacancy_collector.py`
```python
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
```

### `vacancy_parser.py`
```python
SCRAPE_JS = """() => {
  const nodes = document.querySelectorAll('a[data-qa="serp-item__title"]');
  const data = [];
  nodes.forEach(node => {
    if (!node.href.includes('/vacancy/')) return;
    const titleSpan = node.querySelector('span[data-qa="serp-item__title-text"]');
    data.push({
      title: titleSpan ? titleSpan.textContent.trim() : "Unknown",
      link: node.href
    });
  });
  return data;
}
"""


async def scrape_vacancies(page):
    return await page.evaluate(SCRAPE_JS)
```

### `vacancy_writer.py`
```python
import json
import os
import re

VAC_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Vac")
INVALID_FILENAME_CHARS = r'[\\/:*?"<>|]'


def sanitize_filename(name):
    return re.sub(INVALID_FILENAME_CHARS, "_", name).strip().rstrip(".")


def validate_vacancies(vacancies):
    if not isinstance(vacancies, list):
        raise ValueError("vacancies must be a list")
    for v in vacancies:
        if not isinstance(v, dict) or "title" not in v or "link" not in v:
            raise ValueError(f"invalid vacancy item: {v}")
    return len(vacancies)


def summary_message(count, query):
    if count == 0:
        return f"Найдено 0 вакансий"
    return f"Собрано {count} вакансий по названию «{query}». Файл сформирован и загружен."


def write_vacancies(query, vacancies):
    os.makedirs(VAC_FOLDER, exist_ok=True)
    count = validate_vacancies(vacancies)

    safe = sanitize_filename(query.strip())
    base_path = os.path.join(VAC_FOLDER, f"vacancies_{safe}")

    txt_path = base_path + ".txt"
    json_path = base_path + ".json"

    if count > 0:
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(summary_message(count, query) + "\n")
            for i, v in enumerate(vacancies, start=1):
                f.write(f"{i}. {v['title']} — {v['link']}\n")

        data = {
            "query": query,
            "count": count,
            "vacancies": vacancies,
        }
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    else:
        txt_path = None
        json_path = None

    return txt_path, json_path
```

### `vacancy_detail_parser.py`
```python
import re

DETAIL_JS = """() => {
  const text = (sel) => {
    const el = document.querySelector(sel);
    return el ? el.textContent.replace(/\\s+/g, ' ').trim() : null;
  };
  const list = (sel) => {
    return Array.from(document.querySelectorAll(sel)).map(
      (el) => el.textContent.replace(/\\s+/g, ' ').trim()
    );
  };
  const meta = document.querySelector('meta[name="description"]');
  const metaContent = meta ? meta.content : '';

  let salary = text('[data-qa="vacancy-salary-compensation-type-net"]') ||
               text('[data-qa="vacancy-salary-compensation-type-gross"]') ||
               text('[data-qa="vacancy-salary"]');
  if (!salary) {
    const titleEl = document.querySelector('[data-qa="vacancy-title"]');
    if (titleEl && titleEl.parentElement) {
      const spans = titleEl.parentElement.querySelectorAll('span');
      for (const s of spans) {
        const t = s.textContent.replace(/\\s+/g, ' ').trim();
        if (t && /\\d/.test(t)) { salary = t; break; }
      }
    }
  }

  const rawFormat = text('[data-qa="work-formats-text"]') ||
                    text('[data-qa="vacancy-view-remote-work-type"]');

  return {
    title: text('[data-qa="vacancy-title"]'),
    link: location.href,
    company: text('[data-qa="vacancy-company-name"]'),
    salary: salary,
    city: text('[data-qa="vacancy-view-raw-address"]'),
    metro: list('[data-qa="address-metro-station-name"]'),
    experience: text('[data-qa="vacancy-experience"]'),
    employment: text('[data-qa="common-employment-text"]'),
    schedule: text('[data-qa="work-schedule-by-days-text"]'),
    work_hours: text('[data-qa="working-hours-text"]'),
    work_format_raw: rawFormat,
    description: text('[data-qa="vacancy-description"]'),
    skills: list('[data-qa="skills-element"]'),
    meta: metaContent
  };
}
"""


def normalize_work_format(raw):
    if not raw:
        return None
    low = raw.lower()
    if "удален" in low or "удалён" in low:
        return "удаленно"
    if "смешан" in low or "гибрид" in low or "гибк" in low:
        return "гибрид"
    if "на месте" in low or "офис" in low or "работодател" in low:
        return "офис"
    return None


def parse_salary_from_meta(meta):
    if not meta:
        return None
    m = re.search(r"Зарплата:\s*([^.]+)", meta)
    if not m:
        return None
    value = m.group(1).strip()
    if not value or "не указана" in value.lower() or "не указан" in value.lower():
        return None
    return value


def parse_vacancy_result(raw):
    result = dict(raw)
    result["work_format"] = normalize_work_format(raw.get("work_format_raw"))
    if not result.get("salary"):
        result["salary"] = parse_salary_from_meta(raw.get("meta"))
    result.pop("work_format_raw", None)
    result.pop("meta", None)
    link = result.get("link") or ""
    result["link"] = link.split("?")[0]
    return result


async def parse_vacancy_page(page):
    raw = await page.evaluate(DETAIL_JS)
    return parse_vacancy_result(raw)
```

### `details_writer.py`
```python
import json
import os

from vacancy_writer import sanitize_filename

DETAILS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Details")


def _field_lines(vac):
    fields = [
        ("Компания", vac.get("company")),
        ("Зарплата", vac.get("salary")),
        ("Город", vac.get("city")),
        ("Метро", ", ".join(vac.get("metro") or []) or None),
        ("Опыт", vac.get("experience")),
        ("Занятость", vac.get("employment")),
        ("График", vac.get("schedule")),
        ("Рабочие часы", vac.get("work_hours")),
        ("Формат работы", vac.get("work_format")),
        ("Ключевые навыки", ", ".join(vac.get("skills") or []) or None),
    ]
    lines = []
    for name, val in fields:
        if val:
            lines.append(f"- **{name}:** {val}")
        else:
            lines.append(f"- **{name}:** —")
    return lines


def _to_markdown(query, vacancies):
    md = []
    md.append(f"# Вакансии по запросу «{query}»\n")
    for i, vac in enumerate(vacancies, start=1):
        if "error" in vac:
            md.append(f"## {i}. Ошибка загрузки")
            md.append(f"- **Ссылка:** {vac.get('link') or '—'}")
            md.append(f"- **Ошибка:** {vac['error']}")
            md.append("")
            continue
        md.append(f"## {i}. {vac.get('title') or 'Без названия'}")
        md.append(f"- **Ссылка:** {vac.get('link') or '—'}")
        md.extend(_field_lines(vac))
        desc = (vac.get("description") or "").strip()
        md.append("")
        md.append("### Описание")
        md.append(desc if desc else "—")
        md.append("")
    return "\n".join(md)


def write_details(query, vacancies):
    os.makedirs(DETAILS_FOLDER, exist_ok=True)
    safe = sanitize_filename(query)
    base = os.path.join(DETAILS_FOLDER, f"vacancies_details_{safe}")

    json_path = base + ".json"
    md_path = base + ".md"

    data = {
        "query": query,
        "count": len(vacancies),
        "vacancies": vacancies,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(_to_markdown(query, vacancies))

    return json_path, md_path
```

### `tests/test_writer.py`
```python
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vacancy_writer import (
    sanitize_filename,
    summary_message,
    validate_vacancies,
    write_vacancies,
)

import pytest


def test_sanitize_filename():
    assert sanitize_filename('a\\b:c*d?e"f<g>h|i') == "a_b_c_d_e_f_g_h_i"
    assert sanitize_filename("  Разработчик  ") == "Разработчик"


def test_summary_message_nonzero():
    assert summary_message(5, "Python") == (
        "Собрано 5 вакансий по названию «Python». Файл сформирован и загружен."
    )


def test_summary_message_zero():
    assert summary_message(0, "Python") == "Найдено 0 вакансий"


def test_validate_valid_items():
    vacancies = [
        {"title": "a", "link": "https://x"},
        {"title": "b", "link": "https://y"},
    ]
    assert validate_vacancies(vacancies) == 2


def test_validate_invalid_item_raises():
    with pytest.raises(ValueError):
        validate_vacancies([{"title": "a"}])


def test_write_creates_files(tmp_path, monkeypatch):
    monkeypatch.setattr("vacancy_writer.VAC_FOLDER", str(tmp_path))
    vacancies = [
        {"title": "Frontend Developer", "link": "https://hh.ru/vacancy/1"},
    ]
    txt_path, json_path = write_vacancies("Разработчик", vacancies)

    assert txt_path is not None
    assert json_path is not None
    assert os.path.exists(txt_path)
    assert os.path.exists(json_path)

    with open(txt_path, encoding="utf-8") as f:
        content = f.read()
    assert "Собрано 1 вакансий по названию «Разработчик»" in content
    assert "Frontend Developer — https://hh.ru/vacancy/1" in content

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["query"] == "Разработчик"
    assert data["count"] == 1
    assert data["vacancies"][0]["title"] == "Frontend Developer"
    assert data["vacancies"][0]["link"] == "https://hh.ru/vacancy/1"


def test_write_zero_does_not_create_files(tmp_path, monkeypatch):
    monkeypatch.setattr("vacancy_writer.VAC_FOLDER", str(tmp_path))
    txt_path, json_path = write_vacancies("Тест", [])
    assert txt_path is None
    assert json_path is None
    assert os.listdir(tmp_path) == []


def test_vac_folder_created(tmp_path, monkeypatch):
    target = os.path.join(str(tmp_path), "Vac")
    monkeypatch.setattr("vacancy_writer.VAC_FOLDER", target)
    write_vacancies("A", [{"title": "B", "link": "https://hh.ru/vacancy/2"}])
    assert os.path.isdir(target)
```

### `tests/test_e2e.py`
```python
import os
import sys

import pytest
import pytest_asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from playwright.async_api import async_playwright
from vacancy_collector import collect_vacancies

HH_URL = "https://hh.ru"
SEARCH_INPUT = "input[data-qa='search-input']"
VACANCY_ITEM = "a[data-qa='serp-item__title']"
COOKIE_ACCEPT = "[data-qa='cookies-policy-informer-accept']"


@pytest_asyncio.fixture
async def page():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        ctx = await browser.new_context()
        pg = await ctx.new_page()
        yield pg
        await browser.close()


async def _submit_search(page):
    await page.evaluate("""() => {
      const input = document.querySelector('input[data-qa="search-input"]');
      const form = input ? input.closest('form') : null;
      if (form) form.submit();
    }""")


@pytest.mark.asyncio
async def test_navigation_to_hh(page):
    await page.goto(HH_URL, wait_until="domcontentloaded", timeout=60000)
    search = page.locator(SEARCH_INPUT).first
    await search.wait_for(state="visible", timeout=30000)
    assert await search.is_visible()


@pytest.mark.asyncio
async def test_search_flow(page):
    await page.goto(HH_URL, wait_until="domcontentloaded", timeout=60000)
    search = page.locator(SEARCH_INPUT).first
    await search.wait_for(state="visible", timeout=30000)
    await search.fill("frontend")
    await _submit_search(page)
    item = page.locator(VACANCY_ITEM).first
    await item.wait_for(state="visible", timeout=30000)
    assert await item.is_visible()


@pytest.mark.asyncio
async def test_scrape_data_full_page(page):
    """Проверяем, что при пагинации собираются вакансии с нескольких страниц,
    а не только ~20 с первой (lazy loading обработан через переходы по страницам)."""
    await page.goto(HH_URL, wait_until="domcontentloaded", timeout=60000)
    search = page.locator(SEARCH_INPUT).first
    await search.wait_for(state="visible", timeout=30000)
    await search.fill("frontend")
    await _submit_search(page)
    await page.wait_for_selector(VACANCY_ITEM, timeout=30000)

    vacancies = await collect_vacancies(page, "frontend", max_vacancies=40)
    assert len(vacancies) > 20, f"expected >20 vacancies (pagination not handled), got {len(vacancies)}"
    for v in vacancies:
        assert v["title"]
        assert "/vacancy/" in v["link"]
```

---

## 7. История попыток

| № | Подход | Результат |
|---|---|---|
| 1 | LLM-агент (Node.js, AI_Hands) | Провал: парсинг JSON, нестабильные селекторы, «ложный успех» |
| 2 | LLM-агент (Python) | Провал: зацикливание, потеря контекста, капча UI |
| 3 | Детерминированный флоу без LLM | ✅ Работает для простого случая |
| 4 | Подсчёт страниц через `get_total_pages` (h1) | ❌ h1 не содержит числа |
| 5 | Fallback `max_pages = 10` | ❌ Бесконечный/некорректный сбор |
| 6 | Параллельный парсинг деталей (30 волной) | ❌ Капча после ~50 запросов |
| 7 | Последовательный парсинг на одной странице | ✅ Капчи нет |
| 8 | `get_total_vacancies` через `text=Найдено` | ❌ Возвращал 14 вместо 14358 (U+00A0) |
| 9 | Сбор до пустой страницы (старый wait, 25 сек) | ⚠️ Работал, но зависал на пустых/капча-страницах |
| 10 | Правки Клода по `DEBUG_HANDOFF.md` | ✅ Ошибки 1-9 и риски A/B/C |
| 11 | Белый список `ALLOWED_FILTER_PARAMS` (suggestId/hhtm*) | ✅ Чистые URL пагинации |
| 12 | `asyncio.wait_for(_process_page, 15s)` + `page.on("dialog")` | ✅ Корректная остановка за пределами выдачи, без зависаний |
| 13 | **Интерактивная проверка** | ✅ **Скрипт отработал как нужно, проект закрыт** |

---

## 8. Ограничения (важно не нарушать при доработке)

- **Без LLM в рантайме** — только детерминированный Python-код + Playwright.
- **Один браузер-контекст** для сбора списка; никакого параллелизма при навигации.
- **Firefox, не headless** (пользователь видит окно).
- **Селекторы hh.ru** могут меняться — вынесены в константы/JS-скрипты в начале файлов.
- **Windows-терминал** — кириллица: `sys.stdout.reconfigure(encoding="utf-8")` уже есть в `main.py`.
- **HH ограничивает выдачу** — даже если заявлено «14 358», постранично доступно максимум ~100 страниц (~2000 вакансий). `MAX_PAGES_HARD_LIMIT = 100` это учитывает.
- **Белый список `ALLOWED_FILTER_PARAMS`** — если HH добавит новый фильтр, который нужно сохранять при пагинации, ключ нужно добавить в список явно.
- **`[DEBUG] search_url ...` print в main.py** — диагностическая строка, при желании можно убрать (не влияет на работу).
