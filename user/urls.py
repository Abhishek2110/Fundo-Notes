from django.urls import path
from . import views

urlpatterns = [
    path('', views.RegisterApi.as_view(), name='userApi'),
    path('login/', views.LoginApi.as_view(), name='login')
]