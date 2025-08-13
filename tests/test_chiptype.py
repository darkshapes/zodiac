# SPDX-License-Identifier: MPL-2.0 AND LicenseRef-Commons-Clause-License-Condition-1.0
# <!-- // /*  d a r k s h a p e s */ -->

from unittest.mock import patch, MagicMock
import pytest
from enum import Enum
from typing import List, Union, Optional


class MockDevice:
    def __init__(self, device_type):
        self.type = device_type

    def __repr__(self):
        return f"device(type='{self.type}')"

class TestChipTypeXPU:

    @pytest.fixture(scope="function")
    def mock_xpu_available(self):
        with patch("zodiac.providers.constants.first_available", autospec=True) as mock_gpu:
            mock_gpu.return_value = MockDevice("xpu")
            yield mock_gpu

    def test_show_ready(self,mock_xpu_available):
        from zodiac.providers.constants import ChipType

        chip_type = ChipType
        chip_type.initialize_device()
        assert chip_type._show_ready() == [(True, 'XPU',ChipType.XPU[2]),(True, "CPU",ChipType.CPU[2])]

class TestChipTypeCUDA:
    @pytest.fixture(scope="class")
    def mock_cuda_available(self):
        with patch("zodiac.providers.constants.first_available") as mock_gpu:
            mock_gpu.return_value = MockDevice("cuda")
            yield mock_gpu

    def test_show_pkgs(self, mock_cuda_available):
        from zodiac.providers.constants import ChipType
        ChipType.initialize_device()
        # Assuming PkgType is defined and ChipType.initialize_device() sets up the correct state
        packages = ChipType._show_pkgs()
        assert isinstance(packages, list)
        assert packages == ChipType.CUDA[2] + ChipType.CPU[2]

    @pytest.fixture(scope="class")
    def mock_cuda_available_again(self):
        with patch("zodiac.providers.constants.first_available") as mock_gpu:
            mock_gpu.return_value = MockDevice("cuda")
            yield mock_gpu

    def test_api_name_check(self, mock_cuda_available_again):
        from zodiac.providers.constants import ChipType

        # print(ChipType._show_ready(api_name="CUDA"))
        ChipType.initialize_device()
        assert ChipType._show_ready(api_name="CUDA") is True
        assert ChipType._show_ready(api_name="MPS") is False
        assert ChipType._show_ready(api_name="XPU") is False
        assert ChipType._show_ready(api_name="CPU") is True

    def test_show_all(self, mock_cuda_available):
        from zodiac.providers.constants import ChipType

        ChipType.initialize_device()
        assert ChipType._show_all() == ["CUDA", "MPS", "XPU", "MTIA", "CPU"]

# Run the tests
if __name__ == "__main__":
    pytest.main(["-vv", "test_chip_type.py"])
