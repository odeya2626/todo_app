# import sys

# sys.path.append(".")

# from fastapi.testclient import TestClient
# from unittest.mock import MagicMock
# import pytest
# from main import app
# import logging

# logger = logging.getLogger(__name__)


# client = TestClient(app)


# def test_get_login_page():
#     response = client.get("/auth")
#     assert response.status_code == 200
#     assert response.template.name == "login.html"


# it created it on the real db!


# def test_register_new_user():
#     response = client.post(
#         "/auth/register",
#         data={
#             "username": "test",
#             "email": "test@example.com",
#             "password": "password",
#             "password2": "password",
#             "firstname": "test",
#             "lastname": "user",
#         },
#     )
#     assert response.status_code == 200
#     print("response", response.text)
#     assert response.template.name == "login.html"
#     assert response.context["msg"] == "Register successful"
