from services.catalog import models


def test_catalog_loads():
    assert models.load_catalog() >= 20


def test_product_fields_from_catalog():
    p = models.get_product("515291")
    view = models.product_view(p)
    assert view["price"] == p["price"]
    assert view["stock_total"] == sum(p["stock"].values())
    assert any(a["label"] == "Номинальный ток" for a in view["attrs"])


def test_lookup_by_sku_is_case_insensitive():
    assert models.get_by_sku("av-1p-16c")["id"] == "515291"