import samlator
import unittest


class SamlatorTest(unittest.TestCase):
    def test_invalid_test_name(self):
        with self.assertRaisesRegexp(samlator.Error, 'Unknown test: foo'):
            samlator.TestHarness().run_tests(['foo'])


if __name__ == '__main__':
    unittest.main()
