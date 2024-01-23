import unittest
from datetime import datetime, timezone, timedelta
from ulearnProject.utils import get_cbrf_rate


class TestGetCbrfRate(unittest.TestCase):
    def test_with_valid_currency_and_date(self):
        currency = 'USD'
        date = datetime(2022, 1, 1)
        rate = get_cbrf_rate(currency, date)
        self.assertEqual(rate, 74.2926)

    def test_with_invalid_currency(self):
        currency = 'ABC'
        date = datetime(2022, 1, 1)
        rate = get_cbrf_rate(currency, date)
        self.assertIsNone(rate)

    def test_with_rur_currency(self):
        currency = 'RUR'
        date = datetime(2022, 1, 1)
        rate = get_cbrf_rate(currency, date)
        self.assertEqual(rate, 1)


if __name__ == '__main__':
    unittest.main()
