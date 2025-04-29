# #  # # <!-- // /*  SPDX-License-Identifier: LAL-1.3) */ -->
# #  # # <!-- // /*  d a r k s h a p e s */ -->

# # pylint: disable=redefined-outer-name

# from unittest import mock
# import pytest
# import pytest_asyncio

# from package.model_registry import from_ollama_cache
# from package import __main__


# # @pytest.mark.asyncio(loop_scope="session")
# # async def test_model_register(app=__main__.Combo()):
# #     """ """


# @pytest.mark.asyncio(loop_scope="session")
# async def test_model_selected_on_init(app=__main__.Combo()):
#     """Test that a model is available"""
#     models = from_ollama_cache()
#     expected = models[next(iter(models))]
#     async with app.run_test() as pilot:
#         test_element = pilot.app.query_one("#centre-frame")
#         if test_element.is_mounted:
#             assert test_element.current_model == expected


# @pytest_asyncio.fixture(loop_scope="session")
# def mock_generate_response():
#     """Create a decoy chat machine"""
#     with mock.patch("package.fold.ResponsePanel.generate_response", mock.MagicMock()) as mocked:
#         yield mocked


# @pytest.mark.asyncio(loop_scope="session")
# async def test_status_color_remains(app=__main__.Combo()):
#     """Control test for status color reflected in text line"""
#     async with app.run_test() as pilot:
#         expected = frozenset({"tag_line"})
#         assert pilot.app.query_one("#tag_line").classes == expected


# @pytest.mark.asyncio(loop_scope="session")
# async def test_status_color_continues_to_remain(mock_generate_response, app=__main__.Combo()):
#     """Ensure cannot accidentally trigger"""
#     async with app.run_test() as pilot:
#         # ensure no accidental triggers
#         await pilot.press("grave_accent", "tab")
#         expected = frozenset({"tag_line"})
#         assert pilot.app.query_one("#tag_line").classes == expected
#         mock_generate_response.assert_not_called()


# @pytest.mark.asyncio(loop_scope="session")
# async def test_status_color_changes(mock_generate_response, app=__main__.Combo()):
#     """Ensure color changes when activated"""
#     async with app.run_test() as pilot:
#         text_insert = "chunk"
#         pilot.app.query_one("#message_panel").insert(text_insert)
#         pilot.app.query_one("#centre-frame").focus()
#         await pilot.press("tab", "grave_accent")
#         expected = frozenset({"tag_line"})
#         assert pilot.app.query_one("#tag_line").classes == expected

#         # print(pilot.app.query_one("#tag_line").classes)
#         mock_generate_response.assert_called_once()
#         last_model = pilot.app.query_one("#centre-frame").current_model

#         # test color reverts
#         pilot.app.query_one("#centre-frame").current_model = "inactive"
#         # pilot.app.query_one("#centre-frame").is_model_running(False)
#         expected = {"tag_line"}
#         assert pilot.app.query_one("#tag_line").classes == expected
#         mock_generate_response.assert_called_with(last_model, text_insert)
#         print(pilot.app.query_one("#tag_line").classes)

#         pilot.app.exit()
