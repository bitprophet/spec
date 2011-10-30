def setup():
    print 'howdy'

def teardown():
    print 'bye!'

def test_one():
    assert 1 == 1

class TestTwo:
    def setup(self):
        assert "setup" == "setup"
        
    def test_three(self):
        assert 2 == 2

    def test_four(self):
        assert 3 == 3

    def teardown(self):
        assert "teardown" == "teardown"
