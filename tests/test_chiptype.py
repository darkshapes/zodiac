### <!-- // /*  SPDX-License-Identifier: LGPL-3.0  */ -->
### <!-- // /*  d a r k s h a p e s */ -->### <!-- // /*  d a r k s h a p e s */ -->


from unittest.mock import patch, MagicMock
import pytest
from enum import Enum
from typing import List, Union, Optional


class MockDevice:
    def __init__(self, device_type):
        self.type = device_type

    def __repr__(self):
        return f"device(type='{self.type}')"


class TestChipType:
    @pytest.fixture
    def mock_cuda_available(self):
        with patch("zodiac.providers.constants.first_available", autospec=True) as mock_gpu:
            mock_gpu.return_value = MockDevice("cuda")
            yield mock_gpu

    @pytest.fixture
    def mock_xpu_available(self):
        with patch("zodiac.providers.constants.first_available", autospec=True) as mock_gpu:
            mock_gpu.return_value = MockDevice("xpu")
            yield mock_gpu

    def test_show_all(self):
        from zodiac.providers.constants import ChipType

        chip_type = ChipType
        chip_type.initialize_device()
        assert chip_type._show_all() == ["CUDA", "MPS", "XPU", "MTIA", "CPU"]

    def test_show_ready(self, mock_xpu_available):
        from zodiac.providers.constants import ChipType

        chip_type = ChipType
        chip_type.initialize_device()
        assert chip_type._show_ready() == ["XPU", "CPU"]

    def test_show_pkgs(self, mock_cuda_available):
        from zodiac.providers.constants import ChipType

        chip_type = ChipType
        chip_type.initialize_device()
        # Assuming PkgType is defined and ChipType.initialize_device() sets up the correct state
        assert isinstance(chip_type._show_pkgs(), list)

    def test_api_name_check(self, mock_cuda_available):
        from zodiac.providers.constants import ChipType

        chip_type = ChipType
        chip_type.initialize_device()
        assert chip_type._show_ready(api_name="CUDA") is True
        assert chip_type._show_ready(api_name="MPS") is False
        assert chip_type._show_ready(api_name="XPU") is False
        assert chip_type._show_ready(api_name="CPU") is True


# Run the tests
if __name__ == "__main__":
    pytest.main(["-vv", "test_chip_type.py"])
