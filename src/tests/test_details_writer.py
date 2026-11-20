import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from details_writer import DETAILS_FOLDER, write_details

import pytest


def test_write_details_creates_files(tmp_path, monkeypatch):
    monkeypatch.setattr("details_writer.DETAILS_FOLDER", str(tmp_path))
    vacancies = [
        {
            "title": "Frontend",
            "link": "https://hh.ru/vacancy/1",
            "company": "Acme",
            "salary": "от 100 руб",
            "city": "Казань",
            "metro": ["Кремлевская"],
            "experience": "3-6 лет",
            "employment": "Полная",
            "schedule": "5/2",
            "work_hours": "8",
            "work_format": "офис",
            "description": "Текст описания",
            "skills": ["React", "TS"],
        }
    ]
    json_path, md_path = write_details("frontend", vacancies)

    assert os.path.exists(json_path)
    assert os.path.exists(md_path)

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["query"] == "frontend"
    assert data["count"] == 1
    assert data["vacancies"][0]["title"] == "Frontend"
    assert data["vacancies"][0]["skills"] == ["React", "TS"]

    with open(md_path, encoding="utf-8") as f:
        md = f.read()
    assert "## 1. Frontend" in md
    assert "**Формат работы:** офис" in md
    assert "Текст описания" in md


def test_write_details_missing_fields(tmp_path, monkeypatch):
    monkeypatch.setattr("details_writer.DETAILS_FOLDER", str(tmp_path))
    vacancies = [
        {"title": "X", "link": "https://hh.ru/vacancy/2", "description": None, "skills": []}
    ]
    json_path, md_path = write_details("test", vacancies)
    with open(md_path, encoding="utf-8") as f:
        md = f.read()
    assert "**Зарплата:** —" in md
    assert "**Формат работы:** —" in md


def test_write_details_error_item(tmp_path, monkeypatch):
    monkeypatch.setattr("details_writer.DETAILS_FOLDER", str(tmp_path))
    vacancies = [
        {"link": "https://hh.ru/vacancy/3", "error": "Timeout exceeded"},
        {"title": "Ok", "link": "https://hh.ru/vacancy/4", "description": "desc", "skills": []},
    ]
    json_path, md_path = write_details("test", vacancies)
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["count"] == 2
    assert "error" in data["vacancies"][0]
    with open(md_path, encoding="utf-8") as f:
        md = f.read()
    assert "Ошибка загрузки" in md
    assert "## 2. Ok" in md


def test_write_details_empty(tmp_path, monkeypatch):
    monkeypatch.setattr("details_writer.DETAILS_FOLDER", str(tmp_path))
    json_path, md_path = write_details("test", [])
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    assert data["count"] == 0
    assert data["vacancies"] == []
