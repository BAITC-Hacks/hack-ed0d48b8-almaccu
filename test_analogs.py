import pytest

from services.analogs.analogs import find_analogs
from services.catalog import models

OUT_OF_STOCK = ["515292", "520101", "530011", "540002", "550002"]


@pytest.mark.parametrize("pid", OUT_OF_STOCK)
def test_t4_analog_in_stock_with_reason(pid):
    original = models.get_product(pid)
    assert models.total_stock(original) == 0
    analogs = find_analogs(original)
    assert analogs, f"нет аналога для {pid}"
    for a in analogs:
        assert models.total_stock(a["product"]) > 0
        assert a["same"], "у аналога должно быть объяснение, что совпадает"


def test_analog_never_worse_on_hard_params():
    original = models.get_product("515292")  # 1P 25А C 4,5кА
    for a in find_analogs(original):
        attrs = a["product"]["attrs"]
        assert (attrs["current"], attrs["poles"], attrs["curve"]) == (25, 1, "C")
        assert attrs["breaking"] >= 4.5


def test_better_param_is_explained():
    original = models.get_product("520101")  # тип AC
    texts = " ".join(" ".join(a["diffs"]) for a in find_analogs(original))
    assert "это лучше" in texts
