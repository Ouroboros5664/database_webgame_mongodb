import pytest
from flask import Flask
from flask.testing import FlaskClient
from flaskProject.app import app


@pytest.fixture
def client() -> FlaskClient:
    client: FlaskClient = app.test_client()
    return client
