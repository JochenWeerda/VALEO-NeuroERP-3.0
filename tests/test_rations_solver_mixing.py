from __future__ import annotations

from app.agrar.rations.solver.mixing import mix_group_order


def test_mix_group_order_keeps_praxis_sequence() -> None:
    assert mix_group_order("Heu") == 1
    assert mix_group_order("Grassilage") == 2
    assert mix_group_order("Biertreber") == 3
    assert mix_group_order("Mineralfutter") == 5
    assert mix_group_order("Sonderkomponente") == 4
