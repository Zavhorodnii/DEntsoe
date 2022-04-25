from django.urls import path

from getJsonData import views

urlpatterns = [
    path('', views.MainPage.as_view()),
    path('nasdaq/<resource>/', views.GetNasdaqData.as_view()),
    path('day_ahead/<area>/', views.GetDayAheadData.as_view()),
    path('day_ahead_price/<area>/', views.GetDayAheadPriceData.as_view()),
    path('source/<area>/<psrType>/', views.GetCountryData.as_view())
]
