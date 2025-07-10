import unittest


class Calculator:
    def add(self, a, b):
        return a + b

    def multiply(self, a, b):
        return a * b


class TestCalculator(unittest.TestCase):
    def setUp(self):
        self.calc = Calculator()

    def test_add(self):
        self.assertEqual(self.calc.add(2, 3), 5)

    def test_multiply(self):
        self.assertEqual(self.calc.multiply(4, 5), 20)

    def test_add_negative(self):
        self.assertEqual(self.calc.add(-1, 1), 0)


if __name__ == '__main__':
    unittest.main()
