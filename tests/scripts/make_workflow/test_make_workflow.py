import os

import pytest

import definitions
from scripts import make_workflow

TEST_DIR = os.path.join(definitions.TESTS_DIR, 'scripts', 'make_workflow')


class TestMakeWorkflowFromYaml:
    @pytest.mark.skip(reason="not fully implemented.")
    def test_valid_args(self):
        input_path = os.path.join(TEST_DIR, 'valid_input.yml')
        expected = {}
        actual = make_workflow.make_workflow_from_yaml(input_path)
        assert actual == expected

