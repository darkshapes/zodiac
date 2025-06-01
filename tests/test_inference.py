# from mir.registry_entry import RegistryEntry
# from zodiac.chat_machine import BasicImageSignature
# from mir.registry_entry import from_cache
# from mir.constants import LibType
# import asyncio
# from nnll.monitor.file import nfo, dbug
# from zodiac.__main__ import Combo
# from nnll_05 import lookup_function_for
# from nnll_64 import run_inference


# async def test_working_diffusion(app=Combo()):
#     run_inference("model.dit.cogview-3")


# async def test_diffusion(app=Combo()):
#     async with app.run_test() as pilot:
#         run_inference("model.dit.cogview-3")

# @pytest.mark.asyncio(loop_scope="module")

# """Test that the initial state of the app is correct."""

# screen = pilot.app._nodes._get_by_id("fold_screen")

# @pytest.mark.asyncio(loop_scope="module")

# ui_elements = list(pilot.app.query("*"))

# # panel = screen.query_one("#response_panel")
# nfo(f"{pilot.app._nodes._get_by_id('fold_screen')} ")  # {panel}
# tx_data = {"text": "test", "image": None, "speech": None}
# data = from_cache()
# screen.ui["ot"].skip_to("image")
# screen.mode_out = "image"
# screen.next_intent()
# # screen.int_proc.edit_weight(selection="CogView3-Plus-3B", mode_in="text", mode_out="image")
# # screen.next_intent()
# # nfo(screen.int_proc.intent_graph["text"]["image"][5])
# # screen.ui["sl"].on_changed()
# # screen.int_proc.ckpts = [screen.int_proc.intent_graph["text"]["image"][5]]
# constructor, mir_arch = lookup_function_for(screen.int_proc.intent_graph["text"]["image"][5].get("entry").model)
# dbug(constructor, mir_arch)

# screen.tx_data = tx_data
# screen.send_tx()
