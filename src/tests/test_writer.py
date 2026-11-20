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
