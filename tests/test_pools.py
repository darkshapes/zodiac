# # SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# # <!-- // /*  d a r k s h a p e s */ -->


# import pytest
# import pytest_asyncio
# from unittest.mock import AsyncMock, patch, MagicMock
# from enum import Enum


# def has_api(name: str):
#     # Mock implementation that always returns True
#     return True


# class HFCacheInfo:
#     repos: [AsyncMock(repo_id="test/repo")]


# @pytest_asyncio.fixture(loop_scope="module")
# def patch_cache_not_found():
#     return patch("huggingface_hub.CacheNotFound", side_effect=None)


# @pytest_asyncio.fixture(loop_scope="module")
# def patch_hf_cache_info():
#     return patch("huggingface_hub.HFCacheInfo", autospec=True)


# @pytest_asyncio.fixture(loop_scope="module")
# def mock_repo_data():
#     with patch("huggingface_hub.repocard.RepoCard.load", autospec=True) as mocked:
#         mocked.return_value = {"library_name": None}
#         yield mocked


# @pytest_asyncio.fixture(loop_scope="module")
# def mock_mir_db():
#     mocked = MagicMock()
#     mocked.find_path.return_value = None
#     yield mocked


# @pytest.mark.asyncio
# async def test_hub_pool(
#     patch_cache_not_found,
#     patch_hf_cache_info,
#     mock_repo_data,
#     mock_mir_db,
# ):
#     mock_api_data = {"HUB": {"mock_kwargs": "kwargs"}}
#     mock_entries = []

#     # Mock the behavior of mir_db.find_path and other methods

#     from zodiac.providers.pools import hub_pool

#     result = await hub_pool(mock_mir_db, mock_api_data, mock_entries)
#     assert result == mock_entries
