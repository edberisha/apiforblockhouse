from django.test import TestCase
from .models import StockData  

class StockDataModelTests(TestCase):
    def test_stock_data_creation(self):

        stock = StockData.objects.create(
            symbol='AAPL',
            date='2023-01-01',
            open_price=150.0,
            high_price=155.0,
            low_price=148.0,
            close_price=153.0,
            volume=1000000
        )
        self.assertEqual(stock.symbol, 'AAPL')
        self.assertEqual(stock.open_price, 150.0)

class BacktestViewTests(TestCase):
    def setUp(self):
      
        StockData.objects.create(
            symbol='AAPL',
            date='2023-01-01',
            open_price=150.0,
            high_price=155.0,
            low_price=148.0,
            close_price=154.0,
            volume=100000
        )
        StockData.objects.create(
            symbol='AAPL',
            date='2023-01-02',
            open_price=154.0,
            high_price=156.0,
            low_price=152.0,
            close_price=155.0,
            volume=150000
        )

    def test_backtest_view_with_custom_symbol(self):

        response = self.client.post('/backtest/', {
            'initial_investment': 1000,
            'moving_average_short': 1,
            'moving_average_long': 2,
            'stock_symbol': 'AAPL', 
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Return')

    def test_backtest_view(self):
      
        response = self.client.post('/backtest/', {
            'initial_investment': 1000,
            'moving_average_short': 1,
            'moving_average_long': 2
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Total Return')



