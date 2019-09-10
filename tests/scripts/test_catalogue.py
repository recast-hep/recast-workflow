from collections import OrderedDict

import pytest

from scripts import catalogue


class TestGetAllCombinations:
    @pytest.mark.timeout(10)
    def test_no_loops(self):
        catalogue.get_all_combinations()
        assert True

    @pytest.mark.timeout(10)
    def test_correctness(self):
        assert catalogue.get_all_combinations() == [OrderedDict({'generation': 'madgraph_pythia', 'selection': 'rivet', 'statistics': 'pyhf'})]
