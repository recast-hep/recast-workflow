import os

import pytest

import definitions
from scripts import workflow

TEST_DIR = definitions.TESTS_DIR / 'scripts' / 'workflow'


class TestMakeWorkflowFromYaml:
    @pytest.mark.skip(reason="not fully implemented.")
    def test_valid_args(self):
        input_path = os.path.join(TEST_DIR, 'valid_input.yml')
        expected = {}
        actual = workflow.make_workflow_from_yaml(input_path)
        assert actual == expected

