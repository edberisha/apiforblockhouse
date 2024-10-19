from django.db import models
import pickle
import os

class StockData(models.Model):
    symbol = models.CharField(max_length=10)
    date = models.DateField()
    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = (('symbol', 'date'),)  

    def __str__(self):
        return f"{self.symbol} - {self.date}"

    @staticmethod
    def load_model():
        model_path = os.path.join('path/to/your', 'linear_regression_model.pkl')
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model


class StockPrediction(models.Model):
    stock_symbol = models.CharField(max_length=10)
    predicted_price = models.FloatField()
    actual_price = models.FloatField(null=True, blank=True) 
    prediction_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock_symbol} - {self.prediction_date}"