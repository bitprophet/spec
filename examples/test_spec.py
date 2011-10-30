import nose


class TestEmptyDatabase:
    def test_has_current_id_equal_to_1(self):
        pass

    def test_has_no_messages_stored(self):
        assert False # just to show failed test case

    def test_has_at_least_one_user(self):
        pass


class TestFullDatabase:
    def test_raises_an_exception_when_trying_to_add_new_message(self):
        pass

    def test_can_be_extended(self):
        raise nose.DeprecatedTest # just to show deprecated test case
