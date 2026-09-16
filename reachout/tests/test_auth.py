import pytest
import httpx
from unittest.mock import patch

from reachout.tests.conftest import register_manager, login_manager_header


@pytest.mark.anyio
async def test_manager_register_success(client: httpx.AsyncClient):
    request = {
        "email": "testemail@test.com",
        "password": "testpassword"
    }

    response = await client.post("/managers/register", json=request)

    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["email"] == request["email"]


@pytest.mark.anyio
async def test_manager_register_dublicate_email_fails(client: httpx.AsyncClient):
    request = {
            "email": "testemail@test.com",
            "password": "testpassword"
    }

    response = await client.post("/managers/register", json=request)
    response = await client.post("/managers/register", json=request)

    assert response.status_code == 400
    assert response.json()["detail"] == "User already exist"


@pytest.mark.anyio
async def test_manager_login_success(client: httpx.AsyncClient, register_manager):
    request = {
        "username": register_manager["email"],
        "password": register_manager["password"]
    }

    response = await client.post("/managers/login", data=request)

    assert response.status_code == 201
    assert response.json()["token_type"] == "bearer"


@pytest.mark.anyio
async def test_manager_login_wrong(client: httpx.AsyncClient, register_manager):
    request = {
        "username": register_manager["email"],
        "password": "wrong_password"
    }

    response = await client.post("/managers/login", data=request)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect login or password"


@pytest.mark.anyio
async def test_manager_logout_success(client: httpx.AsyncClient, login_manager_header):
    response = await client.post("/managers/logout", headers=login_manager_header)

    assert response.status_code == 200
    assert response.json()["detail"] == "Successfully logged out. Session terminated safely."

    response = await client.get("/managers/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


@pytest.mark.anyio
async def test_add_contacts_success(client: httpx.AsyncClient, login_manager_header):
    request = {
        "items": [
            {
                "first_name": "first_user",
                "email": "one1@example.com",
                "birthday": "1111-11-11",
                "tags": [
                    "string"
                ]
            },
            {
                "first_name": "second_user",
                "email": "two2@example.com",
                "birthday": "2222-22-22",
                "tags": [
                    "string"
                ]
            }
        ]
    }

    response = await client.post("/contacts/add/contacts", json=request, headers=login_manager_header)

    assert response.status_code == 200
    assert response.json()["inserted"] == 2
    assert response.json()["skipped"] == 0


@pytest.mark.anyio
async def test_get_analytic(client: httpx.AsyncClient, login_manager_header):
    response = await client.get("/analytics/", headers=login_manager_header)

    assert response.status_code == 200


@pytest.mark.anyio
async def test_add_campaign(client: httpx.AsyncClient, login_manager_header):
    new_contact = {
        "items": [
            {
                "first_name": "testvipclient",
                "email": "testvipclient@test.com",
                "birthday": "1995-09-17",
                "tags": ["VIP"]
            }
        ]
    }

    new_template = {
        "title": "Promo",
        "body": "new promo!!!"
    }

    await client.post("/contacts/add/contacts", json=new_contact, headers=login_manager_header)
    template_response = await client.post("/templates/add/template", json=new_template, headers=login_manager_header)

    assert template_response.status_code == 200
    assert template_response.json()["title"] == "Promo"

    template_id = template_response.json()["id"]
    campaign_request = {
        "template_id": template_id,
        "target_tag": "VIP",
    }

    with patch("reachout.src.tasks.celery_app.celery_app.send_task") as mock_send_task:
        campaign_response = await client.post("/campaigns/add/task", json=campaign_request, headers=login_manager_header)
        assert campaign_response.status_code == 202
        campaign_id = campaign_response.json()["id"]

        mock_send_task.assert_called_once()

    campaign_add_response = await client.get(f"/campaigns/get/{campaign_id}", headers=login_manager_header)

    assert campaign_add_response.status_code == 200
    assert campaign_add_response.json()["id"] == campaign_id
    