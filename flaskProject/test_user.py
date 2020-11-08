#!/usr/bi6/env python3
import random

from flask.testing import FlaskClient


def test_info(client: FlaskClient):
    response = client.get("/test")
    json = response.get_json()
    print(json)
    assert json["username"] == "qk"


def test_box(client: FlaskClient):
    response = client.get("/qk/box")
    json = response.get_json()
    print(json)
    assert json["name"] == "qk"
    assert json["answer"] == "这是qk的box返回结果："


def test_market(client: FlaskClient):
    response = client.get("/qk/market")
    json = response.get_json()
    print(json)
    assert json["answer"] == "玩家qk查看市场"


def test_wear_success(client: FlaskClient):
    response = client.get("/qk/wear/10级工具")
    json = response.get_json()
    print(json)
    assert json["answer"] == "玩家qk穿戴成功"


def test_wear_fail(client: FlaskClient):
    response = client.get("/qk/wear/11级工具")
    json = response.get_json()
    print(json)
    assert json["error"] == "该宝物名不存在"


def test_wear_fail2(client: FlaskClient):
    response = client.get("/qk/wear/1级工具")
    json = response.get_json()
    print(json)
    assert json["error"] == "存储箱没有该宝物"


def test_buy_success(client: FlaskClient):
    response = client.get("/qk/buy/9级工具")
    json = response.get_json()
    print(json)
    assert json["answer"] == "购买完成，请查看背包"


def test_buy_fail(client: FlaskClient):
    response = client.get("/qk/buy/1级工具")
    json = response.get_json()
    print(json)
    assert json["error"] == "市场无此宝物"


def test_buy_fail2(client: FlaskClient):
    response = client.get("/qk/buy/10级工具")
    json = response.get_json()
    print(json)
    assert json["error"] == "余额不足"


def test_sell_success(client: FlaskClient):
    response = client.get("/qk/sell/10级饰品/1000")
    json = response.get_json()
    print(json)
    assert json["answer"] == "挂牌成功，请查看市场"


def test_sell_fail(client: FlaskClient):
    response = client.get("/qk/sell/11级饰品")
    json = response.get_json()
    print(json)
    assert json["error"] == "存储箱没有该宝物"


def test_withdraw_success(client: FlaskClient):
    response = client.get("/qk/withdraw/10级饰品")
    json = response.get_json()
    print(json)
    assert json["answer"] == "收回成功，请查看背包"


def test_withdraw_fail(client: FlaskClient):
    response = client.get("/qk/withdraw/11级饰品")
    json = response.get_json()
    print(json)
    assert json["error"] == "市场无此宝物"
