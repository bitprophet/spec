def is_even(n):
    return n % 2 == 0

def test_product_of_even_numbers_is_even():
    evens = [(18, 8), (14, 12), (0, 4), (6, 2), (16, 10)]
    for e1, e2 in evens:
        yield check_even, e1, e2

def check_even(e1, e2):
    assert is_even(e1 * e2)
