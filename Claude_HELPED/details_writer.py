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
