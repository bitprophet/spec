from nose.plugins.skip import SkipTest


class TestMyClass(object):
    def test_has_an_attribute(self):
        assert True

    def test_should_perform_some_action(self):
        assert False

    def test_can_stand_on_its_head(self):
        raise SkipTest
