from __future__ import annotations

import json
import threading
from pathlib import Path

# import config

CATEGORY_NAMES = {
    "breaker": "Автоматические выключатели",
    "rcbo": "Дифавтоматы",
    "cable": "Кабель",
    "socket": "Розетки",
    "light": "Освещение",
    "enclosure": "Щиты и аксессуары",
}

ATTR_LABELS = {
    "current": "Номинальный ток",
    "poles": "Число полюсов",
    "curve": "Характеристика срабатывания",
    "breaking": "Отключающая способность",
    "leakage": "Ток утечки",
    "rcd_type": "Тип защиты",
    "cores": "Число жил",
    "section": "Сечение жилы",
    "material": "Материал жилы",
    "ip": "Степень защиты",
    "power": "Мощность",
    "modules": "Число модулей",
}

_lock = threading.Lock()
_products: list[dict] = []
_by_id: dict[str, dict] = {}
_by_sku: dict[str, dict] = {}


def load_catalog(path: Path | str | None = None) -> int:
    """Загружает каталог в память. Возвращает число товаров."""
    path = Path(path or config.CATALOG_PATH)
    data = json.loads(path.read_text(encoding="utf-8"))
    products = data["products"] if isinstance(data, dict) else data
    with _lock:
        _products.clear()
        _by_id.clear()
        _by_sku.clear()
        for p in products:
            p["id"] = str(p["id"])
            p.setdefault("attrs", {})
            p.setdefault("certificates", [])
            p.setdefault("stock", {})
            p.setdefault("unit", "шт")
            _products.append(p)
            _by_id[p["id"]] = p
            if p.get("sku"):
                _by_sku[str(p["sku"]).upper()] = p
    return len(_products)


def _ensure_loaded() -> None:
    if not _products:
        load_catalog()


def all_products() -> list[dict]:
    _ensure_loaded()
    return _products


def get_product(product_id) -> dict | None:
    _ensure_loaded()
    return _by_id.get(str(product_id))


def get_by_sku(sku: str) -> dict | None:
    _ensure_loaded()
    return _by_sku.get(str(sku).upper())


def total_stock(product: dict) -> int:
    return sum(int(q) for q in product.get("stock", {}).values())


def fmt_attr(key: str, value) -> str:
    num = str(value).replace(".", ",")
    return {
        "current": f"{value} А",
        "poles": f"{value}P",
        "breaking": f"{num} кА",
        "leakage": f"{value} мА",
        "section": f"{num} мм²",
        "ip": f"IP{value}",
        "power": f"{value} Вт",
    }.get(key, str(value))


def product_view(p: dict) -> dict:
    """Данные товара для интерфейса. Цена и остаток — только из каталога."""
    return {
        "id": p["id"],
        "sku": p.get("sku", ""),
        "name": p["name"],
        "brand": p.get("brand", ""),
        "category": CATEGORY_NAMES.get(p.get("category"), p.get("category", "")),
        "price": p.get("price"),
        "unit": p.get("unit", "шт"),
        "stock_total": total_stock(p),
        "stock": [{"warehouse": w, "qty": q} for w, q in p.get("stock", {}).items()],
        "attrs": [
            {"label": ATTR_LABELS.get(k, k), "value": fmt_attr(k, v)}
            for k, v in p["attrs"].items()
        ],
        "certificates": p.get("certificates", []),
    }
