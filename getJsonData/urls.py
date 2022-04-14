from django.urls import path

from getJsonData import views

urlpatterns = [
    path('', views.MainPage.as_view()),
    path('<areas>/<source>/', views.GetCountryData.as_view())
]