from services.catalog.ekt_api import extract_items, map_product


def test_map_product_with_lists():
    raw = {
        "id": 515291, "article": "BA47-29", "name": "Автоматический выключатель ВА47-29 1P 16А C",
        "category": "Автоматические выключатели", "price": "1 450,00",
        "stocks": [{"warehouse": "Алматы", "qty": "80"}, {"warehouse": "Астана", "qty": 0}],
        "properties": [{"name": "Номинальный ток, А", "value": "16"}, {"name": "Количество полюсов", "value": "1"},
                       {"name": "Характеристика срабатывания", "value": "c"},
                       {"name": "Отключающая способность, кА", "value": "4,5"}],
        "certificates": [{"name": "Сертификат ТР ТС", "url": "https://example.com/cert.pdf"}],
    }
    p = map_product(raw)
    assert p["id"] == "515291" and p["sku"] == "BA47-29" and p["category"] == "breaker"
    assert p["price"] == 1450 and p["stock"] == {"Алматы": 80, "Астана": 0}
    assert p["attrs"] == {"current": 16, "poles": 1, "curve": "C", "breaking": 4.5}
    assert p["certificates"][0]["url"].endswith("cert.pdf")


def test_map_product_with_dict_stock_and_missing_fields():
    p = map_product({"ID": "9", "title": "Кабель ВВГ 3х2,5", "stock": 120})
    assert p["stock"] == {"Склад": 120} and p["category"] == "cable" and p["certificates"] == []


def test_skip_without_id_or_name():
    assert map_product({"name": "без id"}) is None


def test_extract_items_wrappers():
    assert extract_items({"data": [1]}) == [1]
    assert extract_items([2]) == [2]
    assert extract_items({"unknown": 1}) == []
