import nose

class TestFoobaz(object):
    def test_behaves_such_and_such(self):
        assert True

    def test_causes_an_error(self):
        raise NameError

    def test_fails_to_satisfy_this_specification(self):
        assert False

    def test_throws_deprecated_exception(self):
        raise nose.DeprecatedTest

    def test_throws_skip_test_exception(self):
        raise nose.SkipTest
