import sys

sys.path.append(".")
from unittest.mock import MagicMock
import pytest
from main import app
import logging
from .fixtures import client, app, db_session
from httpx import AsyncClient

logger = logging.getLogger(__name__)


# client = TestClient(app)


@pytest.mark.asyncio
async def test_get_login_page(client: AsyncClient):
    print("client", client)
    response = await client.get("/auth")
    assert response.status_code == 200
    assert response.template.name == "login.html"


# @pytest.mark.asyncio
# async def test_register_new_user(client: AsyncClient):
#     data = (
#         {
#             "username": "test",
#             "email": "test@example.com",
#             "password": "password",
#             "password2": "password",
#             "firstname": "test",
#             "lastname": "user",
#         },
#     )
#     response = await client.post("/auth/register", data=data)
#     assert response.status_code == 200
#     print("response", response.text)
#     assert response.template.name == "login.html"
#     assert response.context["msg"] == "Register successful"
