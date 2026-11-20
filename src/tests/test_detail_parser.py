import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vacancy_detail_parser import normalize_work_format, parse_salary_from_meta, parse_vacancy_result


def test_normalize_office():
    assert normalize_work_format("на месте работодателя") == "офис"
    assert normalize_work_format("Работа в офисе") == "офис"


def test_normalize_remote():
    assert normalize_work_format("удаленно") == "удаленно"
    assert normalize_work_format("Полная удалённая работа") == "удаленно"


def test_normalize_hybrid():
    assert normalize_work_format("смешанный формат") == "гибрид"
    assert normalize_work_format("гибрид") == "гибрид"
    assert normalize_work_format("гибкий график") == "гибрид"


def test_normalize_none():
    assert normalize_work_format(None) is None
    assert normalize_work_format("") is None
    assert normalize_work_format("что-то неопознанное") is None


def test_salary_from_meta_ok():
    meta = "Вакансия X. Зарплата: от 100 000 до 150 000 руб. Казань. Опыт: 3-6 лет."
    assert parse_salary_from_meta(meta) == "от 100 000 до 150 000 руб"


def test_salary_from_meta_not_specified():
    meta = "Вакансия X. Зарплата: не указана. Казань."
    assert parse_salary_from_meta(meta) is None


def test_salary_from_meta_missing():
    assert parse_salary_from_meta(None) is None
    assert parse_salary_from_meta("Зарплата: " ) is None
    assert parse_salary_from_meta("нет данных") is None


def test_parse_vacancy_result_basic():
    raw = {
        "title": "Frontend",
        "link": "https://hh.ru/vacancy/123?query=frontend",
        "company": "Acme",
        "salary": "от 100 руб",
        "city": "Казань",
        "metro": ["Кремлевская"],
        "experience": "3-6 лет",
        "employment": "Полная",
        "schedule": "5/2",
        "work_hours": "8",
        "work_format_raw": "удаленно",
        "description": "Текст описания",
        "skills": ["React", "TS"],
        "meta": "Зарплата: не указана",
    }
    result = parse_vacancy_result(raw)
    assert result["work_format"] == "удаленно"
    assert result["link"] == "https://hh.ru/vacancy/123"
    assert result["salary"] == "от 100 руб"
    assert "work_format_raw" not in result
    assert "meta" not in result


def test_parse_vacancy_result_salary_from_meta():
    raw = {
        "title": "Frontend",
        "link": "https://hh.ru/vacancy/123?query=x",
        "salary": None,
        "work_format_raw": None,
        "meta": "Зарплата: от 50 до 70 руб.",
    }
    result = parse_vacancy_result(raw)
    assert result["salary"] == "от 50 до 70 руб"
    assert result["work_format"] is None
