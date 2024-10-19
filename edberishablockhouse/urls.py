from django.contrib import admin
from django.urls import path
from api.views import backtest, predict_view, report_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('backtest/', backtest, name='backtest'),
    path('predict/', predict_view, name='predict'),  
    path('report/', report_view, name='report'), 


]
