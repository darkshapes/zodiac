# import pytest

# from zodiac.__main__ import Combo
# from zodiac.main_screen import Fold
# from textual.screen import Screen


# @pytest.mark.asyncio(loop_scope="session")
# async def test_responsive_layout(app=Combo()):
#     """Screen rotation function"""
#     async with app.run_test() as pilot:
#         await pilot.resize_terminal(40, 20)
#         expected = "app-grid-horizontal"
#         assert app.query_one("fold_screen").classes == frozenset({expected})

#         await pilot.resize_terminal(39, 20)
#         expected = "app-grid-vertical"
#         assert app.query_children(Screen).classes == frozenset({expected})
