import time

import pytest

from services.cart.cart import CartError, CartService
from services.catalog import models


@pytest.fixture
def stock():
    return {"515291": 10, "530012": 800}


@pytest.fixture
def svc(stock):
    return CartService(stock_lookup=lambda p: stock.get(p["id"], models.total_stock(p)))


def test_t6_propose_does_not_change_cart(svc):
    res = svc.propose_one("s1", "515291", 3)
    assert res["status"] == "needs_confirmation"
    assert svc.count("s1") == 0


def test_t7_confirm_adds_within_stock(svc):
    res = svc.propose_one("s1", "515291", 3)
    svc.confirm("s1", res["action_id"])
    assert svc.lines("s1")[0]["qty"] == 3


def test_t8_qty_capped_by_stock(svc):
    res = svc.propose_one("s1", "515291", 50)
    assert res["lines"][0]["qty"] == 10
    assert res["report"][0]["shortage"] == 40
    svc.confirm("s1")
    res = svc.propose_one("s1", "515291", 1)
    assert res["status"] == "nothing" and res["report"][0]["status"] == "all_in_cart"


def test_out_of_stock_is_reported(svc):
    res = svc.propose_one("s1", "515292", 1)
    assert res["status"] == "nothing" and res["report"][0]["status"] == "out_of_stock"


def test_confirmation_is_single_use(svc):
    res = svc.propose_one("s1", "515291", 1)
    svc.confirm("s1", res["action_id"])
    with pytest.raises(CartError):
        svc.confirm("s1", res["action_id"])


def test_foreign_session_cannot_confirm(svc):
    res = svc.propose_one("s1", "515291", 1)
    with pytest.raises(CartError):
        svc.confirm("attacker", res["action_id"])
    assert svc.count("s1") == 0


def test_cancel(svc):
    svc.propose_one("s1", "515291", 1)
    assert svc.cancel("s1") is True
    with pytest.raises(CartError):
        svc.confirm("s1")


def test_expired(svc):
    svc.ttl = 0
    svc.propose_one("s1", "515291", 1)
    time.sleep(0.01)
    with pytest.raises(CartError):
        svc.confirm("s1")


def test_stock_drop_before_confirm_changes_nothing(svc, stock):
    svc.propose("s1", [("515291", 5), ("530012", 100)])
    stock["515291"] = 2
    with pytest.raises(CartError):
        svc.confirm("s1")
    assert svc.count("s1") == 0  # ни одна строка не добавлена


def test_multi_line_proposal(svc):
    res = svc.propose("s1", [("515291", 2), ("530012", 100), ("515292", 1)])
    assert len(res["lines"]) == 2
    svc.confirm("s1")
    assert svc.count("s1") == 2