def test_good():
    assert True

def test_bad():
    assert False

def test_boom():
    what

def test_skip():
    from nose.plugins.skip import SkipTest
    raise SkipTest
