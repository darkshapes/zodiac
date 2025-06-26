import pytest
from pydantic import BaseModel
from typing import List, Tuple
import re


@pytest.fixture
def sample_registry_entry():
    return RegistryEntry(size=10, tags=["text-to-speech", "image-to-music", "unknown-to-unknown"])


class RegistryEntry(BaseModel):
    size: int
    tags: List[str]

    @property
    def available_tasks(self) -> List[Tuple]:
        pattern = re.compile(r"(\w+)-to-(\w+)")
        processed_tasks = []
        conversion_items = ["text", "speech", "image", "music", "upscale_image", "latent_image", "latent_music"]
        for each_tag in self.tags:
            match = pattern.search(each_tag)
            if match and match.group(1) in conversion_items and match.group(2) in conversion_items:
                processed_tasks.append((match.group(1), match.group(2)))

        return processed_tasks


def test_available_tasks(sample_registry_entry):
    expected_output = [("text", "speech"), ("image", "music")]

    assert sample_registry_entry.available_tasks == expected_output
