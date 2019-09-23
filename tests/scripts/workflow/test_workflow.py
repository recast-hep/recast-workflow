import os

import pytest
import shutil

import definitions
from scripts import workflow

TEST_DIR = definitions.TESTS_DIR / 'scripts' / 'workflow'


class TestExpandWorkflow:
    def test_simple(self):
        breakpoint()
        workflow_path = definitions.SUBWORKFLOWS_DIR / 'selection' / 'rivet' / 'workflow.yml'
        toplevel_path = workflow_path.parent
        actual = workflow.expand_workflow(workflow_path, toplevel_path)
        

class TestMakeWorkflowFromYaml:
    @pytest.mark.skip(reason="not fully implemented.")
    def test_valid_args(self):
        input_path = os.path.join(TEST_DIR, 'valid_input.yml')
        expected = {}
        actual = workflow.make_workflow_from_yaml(input_path)
        assert actual == expected

class TestMakeWorkflow:
    @pytest.mark.skip(reason="not fully implemented.")
    def test_valid_args(self):
        workflows = [('generation', 'madgraph_pythia', {}), ('selection', 'rivet', {}), ('statistics', 'pyhf', {})]
        try:
            output_dir = workflow.make_workflow(workflows)
        finally:
            shutil.rmtree(output_dir, ignore_errors=True)