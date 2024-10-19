from django import forms
from django.core.validators import MinValueValidator, RegexValidator

class BacktestForm(forms.Form):
    initial_investment = forms.FloatField(
        label='Initial Investment',
        validators=[MinValueValidator(0)],
        error_messages={
            'required': 'Please enter your initial investment.',
            'min_value': 'Investment must be greater than zero.'
        }
    )
    moving_average_short = forms.IntegerField(
        label='Short Moving Average',
        validators=[MinValueValidator(1)],
        error_messages={
            'required': 'Please enter a short moving average.',
            'min_value': 'Short moving average must be at least 1.'
        }
    )
    moving_average_long = forms.IntegerField(
        label='Long Moving Average',
        validators=[MinValueValidator(1)],
        error_messages={
            'required': 'Please enter a long moving average.',
            'min_value': 'Long moving average must be at least 1.'
        }
    )
    stock_symbol = forms.CharField(
        max_length=10,
        label='Stock Symbol',
        validators=[RegexValidator(regex='^[A-Za-z]+$', message='Stock symbol must only contain letters.')],
        error_messages={
            'required': 'Please enter a stock symbol.',
            'max_length': 'Stock symbol cannot exceed 10 characters.'
        }
    )
