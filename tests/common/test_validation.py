from common import validation
import pytest


class TestGetInvalidInputs:
    def test_no_input(self):
        assert validation.get_invalid_inputs(
            'generation', 'madgraph_pythia', {}) == {}

    def test_invalid_step(self):
        with pytest.raises(FileNotFoundError):
            assert validation.get_invalid_inputs(
                'fakestep', 'madgraph_pythia', {})

    def test_invalid_workflow_name(self):
        with pytest.raises(FileNotFoundError):
            assert validation.get_invalid_inputs(
                'generation', 'fakeworkflow', {})

    def test_one_invalid_input(self):
        assert validation.get_invalid_inputs('generation', 'madgraph_pythia', {
                                             'fakekey': 'foofum'}) == {'fakekey': 'foofum'}

    def test_two_invalid_input(self):
        assert validation.get_invalid_inputs('generation', 'madgraph_pythia', {
                                             'fakekey1': 'foofum', 'fakekey2': 'foofi'}) == {
            'fakekey1': 'foofum', 'fakekey2': 'foofi'}

    def test_valid_input(self):
        assert validation.get_invalid_inputs('generation', 'madgraph_pythia', {
                                             'fakekey1': 'foofum', 'n_events': 10}) == {
                                             'fakekey1': 'foofum'}


class TestGetMissingInputs:
    def test_all_missing(self):
        assert validation.get_missing_inputs('generation', 'madgraph_pythia', {}) == set(['n_events', 'proc_card'])

    def test_invalid_step(self):
        with pytest.raises(FileNotFoundError):
            assert validation.get_missing_inputs(
                'fakestep', 'madgraph_pythia', {})

    def test_invalid_workflow_name(self):
        with pytest.raises(FileNotFoundError):
            assert validation.get_missing_inputs(
                'generation', 'fakeworkflow', {})

    def test_no_missing(self):
        assert validation.get_missing_inputs('generation', 'madgraph_pythia', {
                                             'n_events': 10, 'proc_card': 'path/to/proc_card', 'ufotar': 'path/to/ufotar'}) == set()
