import pytest
from fastapi.testclient import TestClient
from telegram_bot.main import run_fastapi
from telegram_bot.db.models import Application
from sqlmodel import SQLModel, create_engine, Session
from fastapi import FastAPI

# Фикстура для тестового приложения FastAPI
@pytest.fixture
def app():
    app = FastAPI()
    from telegram_bot.api import all_routers
    for router in all_routers:
        app.include_router(router)
    yield app

# Фикстура для тестового клиента
@pytest.fixture
def client(app):
    return TestClient(app)

def test_create_application(client):
    data = {"name": "Иван", "phone": "79991234567", "comment": "Тестовая заявка"}
    response = client.post("/applications/", json=data)
    assert response.status_code == 201
    result = response.json()
    assert result["name"] == data["name"]
    assert result["phone"] == data["phone"]
    assert result["comment"] == data["comment"]
    assert "id" in result
    assert "created_at" in result

def test_read_applications(client):
    # Сначала создаём заявку
    data = {"name": "Петр", "phone": "79991112233", "comment": "Комментарий"}
    client.post("/applications/", json=data)
    # Получаем список заявок
    response = client.get("/applications/")
    assert response.status_code == 200
    apps = response.json()
    assert isinstance(apps, list)
    assert any(app["name"] == "Петр" for app in apps)

def test_read_application_not_found(client):
    response = client.get("/applications/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Application not found"

def test_delete_application(client):
    # Создаём заявку
    data = {"name": "Удалить", "phone": "79990000000", "comment": "Удалить"}
    resp = client.post("/applications/", json=data)
    app_id = resp.json()["id"]
    # Удаляем заявку
    response = client.delete(f"/applications/{app_id}")
    assert response.status_code == 204
    # Проверяем, что заявка удалена
    response = client.get(f"/applications/{app_id}")
    assert response.status_code == 404 