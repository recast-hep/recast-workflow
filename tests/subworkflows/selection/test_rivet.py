from subworkflows.selection.rivet.common_inputs import get_analyses, is_valid


class TestGetAnalyses:
    def test_no_error(self):
        get_analyses()
        assert True


class TestIsValid:
    def test_no_error(self):
        is_valid('')

    def test_valid(self):
        assert is_valid('1385877')

    def test_invalid(self):
        assert not is_valid('blarg')
