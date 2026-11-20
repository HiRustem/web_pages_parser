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
