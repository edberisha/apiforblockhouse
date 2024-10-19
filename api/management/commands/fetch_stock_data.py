import requests
from django.core.management.base import BaseCommand
from api.models import StockData
from datetime import datetime, timedelta
import os

class Command(BaseCommand):
    help = 'Fetch stock data from Alpha Vantage and store it in the database'

    def add_arguments(self, parser):
        parser.add_argument('symbol', type=str, help='Stock symbol to fetch data for')

    def handle(self, *args, **kwargs):
        symbol = kwargs['symbol']  # Get the symbol from command arguments
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        end_date = datetime.now()
        start_date = end_date - timedelta(days=730)  # 2 years

        url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
        
        response = requests.get(url)
        data = response.json()

        time_series = data.get("Time Series (Daily)", {})
        for date, daily_data in time_series.items():
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            # Only save data if it is within the last two years
            if start_date <= date_obj <= end_date:
                StockData.objects.update_or_create(
                    symbol=symbol,
                    date=date,
                    defaults={
                        'open_price': float(daily_data['1. open']),
                        'high_price': float(daily_data['2. high']),
                        'low_price': float(daily_data['3. low']),
                        'close_price': float(daily_data['4. close']),
                        'volume': int(daily_data['5. volume']),
                    }
                )

        self.stdout.write(self.style.SUCCESS(f'Successfully fetched stock data for {symbol}'))
