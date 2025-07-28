from zodiac.providers.identity import ModelIdentity
from huggingface_hub import scan_cache_dir
import asyncio


def test_model_type():
    model_id = ModelIdentity()
    data = scan_cache_dir()
    if data:
        for repo in data.repos:
            asyncio.run(model_id.find_model_type(repo))
