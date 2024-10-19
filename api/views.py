import pandas as pd
import numpy as np
import requests
from django.shortcuts import render
from django.http import JsonResponse
from .forms import BacktestForm
from .models import StockData
from .models import StockPrediction 
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import pandas as pd
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import joblib  
import matplotlib
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os
from django.core.files.base import ContentFile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from tempfile import NamedTemporaryFile
from django.http import HttpResponse


def fetch_stock_data(symbol):
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)

    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&outputsize=full&apikey={api_key}'
    response = requests.get(url)
    data = response.json()

    time_series = data.get("Time Series (Daily)", {})
    for date, daily_data in time_series.items():
        date_obj = datetime.strptime(date, '%Y-%m-%d')
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


def load_model():
    # Construct the path to the model file
    model_path = os.path.join(os.path.dirname(__file__), 'linear_regression_model.pkl')
    return joblib.load(model_path)

def predict_stock_prices(symbol):
    model = load_model()
    last_days = StockData.objects.filter(symbol=symbol).order_by('-date')[:30]
    
    if last_days.exists():
        df = pd.DataFrame(list(last_days.values('date', 'close_price')))
        df['Days'] = (pd.to_datetime(df['date']) - pd.to_datetime(df['date']).min()).dt.days
        X = df[['Days']].values  # Convert to NumPy array

        predictions = model.predict(X)
        prediction_dates = pd.date_range(start=datetime.now(), periods=30).date
        predicted_prices = pd.DataFrame({'date': prediction_dates, 'predicted_price': predictions})

        return predicted_prices
    return None

def backtest(request):
    result = None  

    if request.method == 'POST':
        form = BacktestForm(request.POST)
        print("Received POST data:", request.POST) 

        if form.is_valid():
            initial_investment = float(form.cleaned_data['initial_investment'])
            short_ma = form.cleaned_data['moving_average_short']
            long_ma = form.cleaned_data['moving_average_long']
            stock_symbol = form.cleaned_data['stock_symbol']

            if not StockData.objects.filter(symbol=stock_symbol).exists():
                fetch_stock_data(stock_symbol)

            data = StockData.objects.filter(symbol=stock_symbol).order_by('date')
            df = pd.DataFrame(list(data.values('date', 'close_price')))

            if df.empty:
                return JsonResponse({'error': 'No data found for the specified symbol.'}, status=400)

            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df['short_moving_average'] = df['close_price'].rolling(window=short_ma).mean()
            df['long_moving_average'] = df['close_price'].rolling(window=long_ma).mean()

            df['close_price'] = df['close_price'].astype(float)
            df['signal'] = np.where(df['short_moving_average'] > df['long_moving_average'], 1, 0)
            df['position'] = df['signal'].diff()

            investment_value = initial_investment
            num_trades = 0
            position_value = 0

            for i in range(len(df)):
                if df['position'].iloc[i] == 1:  
                    position_value = investment_value / df['close_price'].iloc[i]
                    investment_value = 0
                    num_trades += 1
                elif df['position'].iloc[i] == -1 and investment_value == 0: 
                    investment_value = position_value * df['close_price'].iloc[i]
                    position_value = 0
                    num_trades += 1

            total_value = investment_value + (position_value * df['close_price'].iloc[-1] if position_value else 0)
            total_return = total_value - initial_investment

            result = {
                'total_return': float(total_return),
                'number_of_trades': int(num_trades),
            }

            return JsonResponse(result)
        else:
            print("Form errors:", form.errors) 

    else:
        form = BacktestForm()

    return render(request, 'api/backtest.html', {'form': form, 'result': result})




def create_plot(actual_prices, predicted_prices_df):
    plt.figure(figsize=(10, 5))
    plt.plot(actual_prices['date'], actual_prices['close_price'], label='Actual Prices', color='blue')
    plt.plot(predicted_prices_df['date'], predicted_prices_df['predicted_price'], label='Predicted Prices', color='orange')
    plt.title('Stock Price Prediction vs Actual')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    plt.close()  
    return img_buf


def predict_view(request):
    if request.method == 'POST':
        print(request.POST)  
        stock_symbol = request.POST.get('stock_symbol')

        if not StockData.objects.filter(symbol=stock_symbol).exists():
            fetch_stock_data(stock_symbol)

        predicted_prices = predict_stock_prices(stock_symbol)
        
        if predicted_prices is not None:
            for _, row in predicted_prices.iterrows():
                StockPrediction.objects.update_or_create(
                    stock_symbol=stock_symbol,
                    predicted_price=row['predicted_price'],
                    prediction_date=row['date']
                )
            return JsonResponse(predicted_prices.to_dict(orient='records'), safe=False)
        else:
            return JsonResponse({'error': 'No predictions could be made.'}, status=400)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def generate_report(stock_symbol):
    actual_data = StockData.objects.filter(symbol=stock_symbol).order_by('date')
    predicted_data = StockPrediction.objects.filter(stock_symbol=stock_symbol).order_by('prediction_date')
    
    actual_df = pd.DataFrame(list(actual_data.values('date', 'close_price')))
    predicted_df = pd.DataFrame(list(predicted_data.values('prediction_date', 'predicted_price')))
    
    plt.figure(figsize=(10, 5))
    plt.plot(actual_df['date'], actual_df['close_price'], label='Actual Prices', color='blue')
    plt.plot(predicted_df['prediction_date'], predicted_df['predicted_price'], label='Predicted Prices', color='orange')
    plt.title(f'Stock Price Prediction vs Actual: {stock_symbol}')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    img_buf = BytesIO()
    plt.savefig(img_buf, format='png')
    img_buf.seek(0)
    
    return actual_df, predicted_df, img_buf


def create_pdf_report(stock_symbol, img_buf):
    with NamedTemporaryFile(delete=True, suffix='.png') as tmp_file:
        tmp_file.write(img_buf.getvalue())
        tmp_file.flush()  

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{stock_symbol}_report.pdf"'
        
        p = canvas.Canvas(response, pagesize=letter)
        p.drawString(100, 750, f'Report for {stock_symbol}')
        
        p.drawImage(tmp_file.name, 50, 300, width=500, height=250)
        
        p.showPage()
        p.save()
        
        return response


def report_view(request):
    if request.method == 'POST':
        stock_symbol = request.POST.get('stock_symbol')
        print(f"Received stock symbol: {stock_symbol}") 

        actual_data = StockData.objects.filter(symbol=stock_symbol).order_by('date')
        actual_prices = pd.DataFrame(list(actual_data.values('date', 'close_price')))

        predicted_prices = predict_stock_prices(stock_symbol)
        if predicted_prices is None:
            print("No predictions available.") 
            return JsonResponse({'error': 'No predictions available.'}, status=400)

        predicted_prices_df = pd.DataFrame(predicted_prices)

        img_buf = create_plot(actual_prices, predicted_prices_df)
        return create_pdf_report(stock_symbol, img_buf)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def favicon(request):
    return HttpResponse(status=204)