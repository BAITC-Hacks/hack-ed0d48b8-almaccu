"""Первая выгрузка каталога и разведка структуры API.

Запуск:  python -m scripts.sync_catalog --pages 3 --details 10
Сохраняет сырые ответы в data/raw/ и печатает, какие поля реально приходят.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

# from services.catalog.ekt_client import EktClient

RAW_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pages", type=int, default=2, help="сколько страниц списка выгрузить")
    parser.add_argument("--details", type=int, default=5, help="сколько детальных карточек выгрузить")
    args = parser.parse_args()

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    client = EktClient()

    products = list(client.iter_products(max_pages=args.pages))
    (RAW_DIR / "products.json").write_text(
        json.dumps(products, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"Товаров в списке: {len(products)}")
    list_fields = Counter(k for p in products if isinstance(p, dict) for k in p)
    print("Поля в списке:", dict(list_fields.most_common()))

    details = []
    for p in products[: args.details]:
        pid = p.get("id") if isinstance(p, dict) else None
        if pid is not None:
            details.append(client.get_product_detail(pid))
    (RAW_DIR / "details.json").write_text(
        json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    detail_fields = Counter(k for d in details if isinstance(d, dict) for k in d)
    print(f"Детальных карточек: {len(details)}")
    print("Поля в карточке:", dict(detail_fields.most_common()))


if __name__ == "__main__":
    main()