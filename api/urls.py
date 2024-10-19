from django.urls import path
from api.views import backtest, predict_view, report_view, favicon

urlpatterns = [
    path('', backtest, name='root'),  
    path('backtest/', backtest, name='backtest'),
    path('predict/', predict_view, name='predict'),
    path('generate-report/', report_view, name='generate_report'),
    path('report/', report_view, name='report'),  
    path('favicon.ico', favicon, name='favicon'),  
]
