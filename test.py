def test_good():
    assert True

def test_bad():
    assert False

def test_boom():
    what

def test_skip():
    from nose.plugins.skip import SkipTest
    raise SkipTest


class Foo(object):
    def has_no_underscore(self):
        assert True

    def has_no_Test(self):
        assert True

class Foo_(object):
    def should_print_out_as_Foo(self):
        pass
