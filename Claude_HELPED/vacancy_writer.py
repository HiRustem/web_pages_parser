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
