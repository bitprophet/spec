def test():
    print "FOO test FOO"

class TestOutputSave:
    def setup(self):
        print "BAR OutputTest.setup BAR"

    def test(self):
        print "BAR OutputTest.test BAR"

    def teardown(self):
        print "BAR OutputTest.teardown BAR"

def test_fail():
    print 'FIBBLE'
    assert 0

def test_error():
    print 'BLOOBLE'
    raise Exception
