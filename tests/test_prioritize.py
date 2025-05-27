# type: ignore
import pytest
from textual.containers import Container, Horizontal  # noqa

from zodiac.__main__ import Combo
from test_graph import mock_ollama_data, mock_hub_data, test_mocked_hub, test_mocked_ollama, test_create_graph


@pytest.mark.asyncio(loop_scope="module")
async def test_top_priority_single(mock_ollama_data, mock_hub_data, app=Combo()):
    # add star and move to top
    from nnll_01 import nfo
    import sys
    import os

    async with app.run_test() as pilot:
        screen_id = pilot.app._nodes._get_by_id("fold_screen")
        nfo(screen_id.int_proc.models)
        nfo(screen_id.int_proc.ckpts)
        zero_order = {}
        for i, model in enumerate(screen_id.int_proc.ckpts):
            zero_order.setdefault(i, model)  # test control original order
            screen_id.int_proc.ckpts[i]["weight"] = 1.0

        floor = len(screen_id.int_proc.ckpts) - 1
        screen_id.int_proc.ckpts[floor]["weight"] = 0.9
        screen_id.int_proc.set_ckpts()
        model_id = zero_order[floor]["entry"].model
        nfo(screen_id.int_proc.ckpts)
        assert (f"*{os.path.basename(model_id)}", model_id) == screen_id.int_proc.models[0]


@pytest.mark.asyncio(loop_scope="module")
async def test_top_priority_multiple_value_add_star(mock_ollama_data, mock_hub_data, app=Combo()):
    # add star and move to top
    from nnll_01 import nfo
    import sys
    import os

    async with app.run_test() as pilot:
        screen_id = pilot.app._nodes._get_by_id("fold_screen")

        nfo(screen_id.int_proc.models)
        nfo(screen_id.int_proc.ckpts)
        zero_order = {}
        for i, model in enumerate(screen_id.int_proc.ckpts):
            zero_order.setdefault(i, model)  # test control original order
            screen_id.int_proc.ckpts[i]["weight"] = 1.0

        floor = len(screen_id.int_proc.ckpts) - 2
        assert screen_id.int_proc.ckpts[floor]["weight"] == 1.0
        screen_id.int_proc.ckpts[floor]["weight"] = 0.9

        screen_id.int_proc.set_ckpts()

        model_id_1 = zero_order[floor]["entry"].model
        nfo(f"model 1 changed to 0.9{model_id_1}")
        assert "gemma" in model_id_1

        floor = len(screen_id.int_proc.ckpts) - 1
        assert screen_id.int_proc.ckpts[floor]["weight"] == 1.0
        screen_id.int_proc.ckpts[floor]["weight"] = 0.9

        screen_id.int_proc.set_ckpts()
        model_id_2 = zero_order[floor]["entry"].model
        assert "reka" in model_id_2
        nfo(f"model 2 changed to 0.9{model_id_2}")
        nfo(screen_id.int_proc.ckpts)
        model_prev_top = zero_order[0]["entry"].model
        assert [(f"*{os.path.basename(model_id_1)}", model_id_1), (f"*{os.path.basename(model_id_2)}", model_id_2), (f"{os.path.basename(model_prev_top)}", model_prev_top)] == screen_id.int_proc.models
