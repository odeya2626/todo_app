import sys

sys.path.append(".")

from httpx import AsyncClient
from starlette.testclient import TestClient

from main import app

from .fixtures import client, db_session


async def test_login_not_registered(client: AsyncClient):
    print("test_login_not_registered")
    payload = {"username": "admin", "password": "admin"}
    response = await client.post("/auth/", data=payload)
    print(response)
    assert response.status_code == 200
