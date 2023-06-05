from typing import List, Optional

import pytest
import typeguard

from labelcomposer.helpers import check_type_bool


@typeguard.typechecked
class TestTypecheck:
    def test_basic_types(self):
        assert check_type_bool(4, int)
        assert not check_type_bool(4, str)

    def test_sequence_types(self):
        assert check_type_bool([4, 5, 6], List[int])
        assert not check_type_bool(["A", 5, 6], List[int])
        assert not check_type_bool(
            [5, 6, "A"],
            List[int],
            collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS,
        )

    def test_optional(self):
        assert not check_type_bool("A", Optional[int])
        assert not check_type_bool(
            [5, 6, "A"],
            List[int],
            collection_check_strategy=typeguard.CollectionCheckStrategy.ALL_ITEMS,
        )

    def test_optional(self):
        assert not check_type_bool("A", Optional[int])
